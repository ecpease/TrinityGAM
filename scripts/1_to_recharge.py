import geopandas as gpd
import os
import numpy as np
from osgeo import gdal
import pandas as pd


# read in shapefile from Texas Water Development Board https://www.twdb.texas.gov/groundwater/models/gam/glfc_n/glfc_n.asp
# Shapefile is also available on GitHub TrinityGAM repository in GIS folder
df = gpd.read_file(os.path.join('GIS','clip_final.shp'))
# df = pd.read_csv(os.path.join('GIS','trnt_n_grid.csv')) # converted the shp to csv that is smaller and easier to load with pd instead of gpd.
print(df.head())
print('loaded shp')

nrow, ncol = df['ROW'].max(), df['COL'].max() # nrow and ncol are the maximum number of row and col in this case. 
print(nrow,ncol)

delr, delc = 5280, 5280 # mile x mile in feet
nlay = 8 # 8 layers in model, but not important

def get_raster_value(xcoords,ycoords,nrow,ncol,mfrows,mfcols,raster_path,name='name'):
    """
    :param xcoords:
    :param ycoords:
    :param nrow:
    :param ncol:
    :param mfrows:
    :param mfcols:
    :param raster_path:
    :param name:
    :return:

    Written by Ross Kushnereit
    INTERA, Inc.

    This function converts a raster to a NumPy array.  Then resizes it to match the model array.
    """
    dataset = gdal.Open(raster_path)
    band = dataset.GetRasterBand(1)
    cols, rows = dataset.RasterXSize, dataset.RasterYSize
    transform = dataset.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = -transform[5]
    data = np.array(band.ReadAsArray(0, 0, cols, rows))
    print(data.shape)
    array = np.ones((nrow,ncol)) * -12345
    for i in range(len(xcoords)):
        if (xcoords[i]>xOrigin) and (yOrigin > ycoords[i]):# and (xcoords[i]<(xOrigin+ncol*pixelWidth)) and (yOrigin+nrow*pixelHeight < ycoords[i]):
            try:
                col = abs(int((xcoords[i] - xOrigin) / pixelWidth))
                row = abs(int((yOrigin - ycoords[i]) / pixelHeight))
                r, c = int(mfrows[i]-1), int(mfcols[i]-1)
                print(r,c, 'r,c')
                v = data[row, col]
                array[r, c] = v
            except:
                pass

    array[array<=-12345] = np.nan
    return array

# .tif comes from PRISM.  We clipped it to make the script run faster
raster_path = os.path.join('..', 'GIS','annual_30_prism.tif')
array = get_raster_value(df['CentroidX'],df['CentroidY'],nrow,ncol,df['ROW'],df['COL'],raster_path=raster_path,name='prism')

np.savetxt('prism_mean_rch.txt',array)
