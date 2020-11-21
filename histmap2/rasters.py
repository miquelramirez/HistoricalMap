"""!@brief Manage data (opening/saving raster, get ROI...)"""
# -*- coding: utf-8 -*-

import scipy as sp
from osgeo import gdal

def open_data_band(filename):
    """!@brief The function open and load the image given its name. 
    The function open and load the image given its name. 
    The type of the data is checked from the file and the scipy array is initialized accordingly.
        Input:
            filename: the name of the file
        Output:
            data : the opened data with gdal.Open() method
            im : empty table with right dimension (array)
    
    """
    data = gdal.Open(filename,gdal.GA_ReadOnly)
    if data is None:
        print('Impossible to open '+filename)
        exit()
    nc = data.RasterXSize
    nl = data.RasterYSize
#    d  = data.RasterCount
    
    # Get the type of the data
    gdal_dt = data.GetRasterBand(1).DataType
    if gdal_dt == gdal.GDT_Byte:
        dt = 'uint8'
    elif gdal_dt == gdal.GDT_Int16:
        dt = 'int16'
    elif gdal_dt == gdal.GDT_UInt16:
        dt = 'uint16'
    elif gdal_dt == gdal.GDT_Int32:
        dt = 'int32'
    elif gdal_dt == gdal.GDT_UInt32:
        dt = 'uint32'
    elif gdal_dt == gdal.GDT_Float32:
        dt = 'float32'
    elif gdal_dt == gdal.GDT_Float64:
        dt = 'float64'
    elif gdal_dt == gdal.GDT_CInt16 or gdal_dt == gdal.GDT_CInt32 or gdal_dt == gdal.GDT_CFloat32 or gdal_dt == gdal.GDT_CFloat64 :
        dt = 'complex64'
    else:
        print('Data type unkown')
        exit()
    
    # Initialize the array
    im = sp.empty((nl,nc),dtype=dt) 
    return data,im

'''
Old function that open all the bands
'''
#    
#    for i in range(d):
#        im[:,:,i]=data.GetRasterBand(i+1).ReadAsArray()
#    
#    GeoTransform = data.GetGeoTransform()
#    Projection = data.GetProjection()
#    data = None


def create_empty_tiff(outname,im,d,GeoTransform,Projection):
    '''!@brief Write an empty image on the hard drive.
    
    Input: 
        outname: the name of the file to be written
        im: the image cube
        GeoTransform: the geotransform information 
        Projection: the projection information
    Output:
        Nothing --
    '''
    nl = im.shape[0]
    nc = im.shape[1]

    driver = gdal.GetDriverByName('GTiff')
    dt = im.dtype.name
    # Get the data type
    if dt == 'bool' or dt == 'uint8':
        gdal_dt=gdal.GDT_Byte
    elif dt == 'int8' or dt == 'int16':
        gdal_dt=gdal.GDT_Int16
    elif dt == 'uint16':
        gdal_dt=gdal.GDT_UInt16
    elif dt == 'int32':
        gdal_dt=gdal.GDT_Int32
    elif dt == 'uint32':
        gdal_dt=gdal.GDT_UInt32
    elif dt == 'int64' or dt == 'uint64' or dt == 'float16' or dt == 'float32':
        gdal_dt=gdal.GDT_Float32
    elif dt == 'float64':
        gdal_dt=gdal.GDT_Float64
    elif dt == 'complex64':
        gdal_dt=gdal.GDT_CFloat64
    else:
        print('Data type non-suported')
        exit()
    
    dst_ds = driver.Create(outname,nc,nl, d, gdal_dt)
    dst_ds.SetGeoTransform(GeoTransform)
    dst_ds.SetProjection(Projection)
    
    return dst_ds
    
    '''
    Old function that cannot manage to write on each band outside the script
    '''
#    if d==1:
#        out = dst_ds.GetRasterBand(1)
#        out.WriteArray(im)
#        out.FlushCache()
#    else:
#        for i in range(d):
#            out = dst_ds.GetRasterBand(i+1)
#            out.WriteArray(im[:,:,i])
#            out.FlushCache()
#    dst_ds = None
    
def get_samples_from_roi(raster_name,roi_name):
    '''!@brief Get the set of pixels given the thematic map.
    Get the set of pixels given the thematic map. Both map should be of same size. Data is read per block.
        Input:
            raster_name: the name of the raster file, could be any file that GDAL can open
            roi_name: the name of the thematic image: each pixel whose values is greater than 0 is returned
        Output:
            X: the sample matrix. A nXd matrix, where n is the number of referenced pixels and d is the number of variables. Each 
                line of the matrix is a pixel.
            Y: the label of the pixel
    Written by Mathieu Fauvel.
    ''' 
    
    ## Open Raster
    raster = gdal.Open(raster_name,gdal.GA_ReadOnly)
    if raster is None:
        print( 'Impossible to open '+raster_name)
        exit()

    ## Open ROI
    roi = gdal.Open(roi_name,gdal.GA_ReadOnly)
    if roi is None:
        print( 'Impossible to open '+roi_name)
        exit()

    ## Some tests
    if (raster.RasterXSize != roi.RasterXSize) or (raster.RasterYSize != roi.RasterYSize):
        print( 'Images should be of the same size')
        exit()

    ## Get block size
    band = raster.GetRasterBand(1)
    block_sizes = band.GetBlockSize()
    x_block_size = block_sizes[0]
    y_block_size = block_sizes[1]
    del band
    
    ## Get the number of variables and the size of the images
    d  = raster.RasterCount
    nc = raster.RasterXSize
    nl = raster.RasterYSize

    ## Read block data
    X = sp.array([]).reshape(0,d)
    Y = sp.array([]).reshape(0,1)
    for i in range(0,nl,y_block_size):
        if i + y_block_size < nl: # Check for size consistency in Y
            lines = y_block_size
        else:
            lines = nl - i
        for j in range(0,nc,x_block_size): # Check for size consistency in X
            if j + x_block_size < nc:
                cols = x_block_size
            else:
                cols = nc - j

            # Load the reference data
            
            ROI = roi.GetRasterBand(1).ReadAsArray(j, i, cols, lines)
            
            t = sp.nonzero(ROI)
            
            if t[0].size > 0:
                Y = sp.concatenate((Y,ROI[t].reshape((t[0].shape[0],1)).astype('uint8')))
                # Load the Variables
                Xtp = sp.empty((t[0].shape[0],d))
                for k in range(d):
                    band = raster.GetRasterBand(k+1).ReadAsArray(j, i, cols, lines)
                    Xtp[:,k] = band[t]
                try:
                    X = sp.concatenate((X,Xtp))
                except MemoryError:
                    print( 'Impossible to allocate memory: ROI too big')
                    exit()
    
    # Clean/Close variables
    del Xtp,band    
    roi = None # Close the roi file
    raster = None # Close the raster file

    return X,Y

def predict_image(raster_name,classif_name,classifier,mask_name=None):
    """!@brief Classify the whole raster image, using per block image analysis
        The classifier is given in classifier and options in kwargs.
        
        Input:
            raster_name (str)
            classif_name (str)
            classifier (str)
            mask_name(str)
            
        Return:
            Nothing but raster written on disk
        Written by Mathieu Fauvel.
    """
    # Parameters
    block_sizes = 512

    # Open Raster and get additionnal information
    raster = gdal.Open(raster_name,gdal.GA_ReadOnly)
    if raster is None:
        print( 'Impossible to open '+raster_name)
        exit()
    
    # If provided, open mask
    if mask_name is None:
        mask=None
    else:
        mask = gdal.Open(mask_name,gdal.GA_ReadOnly)
        if mask is None:
            print( 'Impossible to open '+mask_name)
            exit()
        # Check size
        if (raster.RasterXSize != mask.RasterXSize) or (raster.RasterYSize != mask.RasterYSize):
            print( 'Image and mask should be of the same size')
            exit()   
        
    # Get the size of the image
    d  = raster.RasterCount
    nc = raster.RasterXSize
    nl = raster.RasterYSize
    
    # Get the geoinformation    
    GeoTransform = raster.GetGeoTransform()
    Projection = raster.GetProjection()
    
    # Set the block size 
    x_block_size = block_sizes  
    y_block_size = block_sizes
    
    ## Initialize the output
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(classif_name, nc,nl, 1, gdal.GDT_UInt16)
    dst_ds.SetGeoTransform(GeoTransform)
    dst_ds.SetProjection(Projection)
    out = dst_ds.GetRasterBand(1)
    
    ## Set the classifiers
    if classifier['name'] is 'NPFS':
        ## With GMM
        model = classifier['model']
        ids = classifier['ids']
        nv = len(ids)
    elif classifier['name'] is 'GMM':
        model = classifier['model']   
    
    ## Perform the classification
    for i in range(0,nl,y_block_size):
        if i + y_block_size < nl: # Check for size consistency in Y
            lines = y_block_size
        else:
            lines = nl - i
        for j in range(0,nc,x_block_size): # Check for size consistency in X
            if j + x_block_size < nc:
                cols = x_block_size
            else:
                cols = nc - j
                       
            # Do the prediction
            if classifier['name'] is 'NPFS':
                # Load the data
                X = sp.empty((cols*lines,nv))
                for ind,v in enumerate(ids):
                    X[:,ind] = raster.GetRasterBand(int(v+1)).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
                
                # Do the prediction
                if mask is None:
                    yp = model.predict_gmm(X)[0].astype('uint16')
                else:
                    mask_temp=mask.GetRasterBand(1).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
                    t = sp.where(mask_temp!=0)[0]
                    yp=sp.zeros((cols*lines,))
                    yp[t]= model.predict_gmm(X[t,:])[0].astype('uint16')
                    
            elif classifier['name'] is 'GMM':
                # Load the data
                X = sp.empty((cols*lines,d))
                for ind in range(d):
                    X[:,ind] = raster.GetRasterBand(int(ind+1)).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
                
                # Do the prediction
                if mask is None:
                    yp = model.predict_gmm(X)[0].astype('uint16')
                else:
                    mask_temp=mask.GetRasterBand(1).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
                    t = sp.where(mask_temp!=0)[0]
                    yp=sp.zeros((cols*lines,))
                    yp[t]= model.predict_gmm(X[t,:])[0].astype('uint16')
                
            # Write the data
            out.WriteArray(yp.reshape(lines,cols),j,i)
            out.FlushCache()
            del X,yp

    # Clean/Close variables    
    raster = None
    dst_ds = None

def smooth_image(raster_name,mask_name,output_name,l,t):
    """!@brief Apply a smoothing filter on all the pixels of the input image
   
    Input:
        raster_name: the name of the originale SITS
        mask_name: the name of the mask. In that file, every pixel with value greater than 0 is masked.
        output_name: the name of the smoothed image
    
    TO DO: 
    - check the input file format (uint16 or float)
    - parallelization
    
    Written by Mathieu Fauvel
    """
    # Get 
    import smoother as sm
    # Open Raster and get additionnal information
    raster = gdal.Open(raster_name,gdal.GA_ReadOnly)
    if raster is None:
        print( 'Impossible to open '+raster_name)
        exit()

    # Open Mask and get additionnal information
    mask = gdal.Open(mask_name,gdal.GA_ReadOnly)
    if raster is None:
        print( 'Impossible to open '+mask_name)
        exit()

    # Check size
    if (raster.RasterXSize != mask.RasterXSize) or (raster.RasterYSize != mask.RasterYSize) or (raster.RasterCount != mask.RasterCount):
        print( 'Image and mask should be of the same size')
        exit() 
    
    # Get the size of the image
    d  = raster.RasterCount
    nc = raster.RasterXSize
    nl = raster.RasterYSize

    # Get the geoinformation    
    GeoTransform = raster.GetGeoTransform()
    Projection = raster.GetProjection()

    # Get block size
    band = raster.GetRasterBand(1)
    block_sizes = band.GetBlockSize()
    x_block_size = block_sizes[0]
    y_block_size = block_sizes[1]
    del band

    # Initialize the output
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(output_name, nc,nl, d, gdal.GDT_Float64)
    dst_ds.SetGeoTransform(GeoTransform)
    dst_ds.SetProjection(Projection)

    for i in range(0,nl,y_block_size):
        if i + y_block_size < nl: # Check for size consistency in Y
            lines = y_block_size
        else:
            lines = nl - i
        for j in range(0,nc,x_block_size): # Check for size consistency in X
            if j + x_block_size < nc:
                cols = x_block_size
            else:
                cols = nc - j

            # Get the data
            X = sp.empty((cols*lines,d))
            M = sp.empty((cols*lines,d),dtype='int')
            for ind in range(d):
                X[:,ind] = raster.GetRasterBand(int(ind+1)).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
                M[:,ind] = mask.GetRasterBand(int(ind+1)).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
            # Put all masked value to 1
            M[M>0]=1
            
            # Do the smoothing
            Xf = sp.empty((cols*lines,d))
            for ind in range(cols*lines): # This part can be speed up by doint it in parallel
                smoother = sm.Whittaker(x=X[ind,:],t=t,w=1-M[ind,:],order=2)
                Xf[ind,:] = smoother.smooth(l)

            # Write the data
            for ind in range(d):
                out = dst_ds.GetRasterBand(ind+1)
                out.WriteArray(Xf[:,ind].reshape(lines,cols),j,i)
                out.FlushCache()

            # Free memory
            del X,Xf,M,out

    # Clean/Close variables
    raster = None
    mask = None
    dst_ds = None

