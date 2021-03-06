#!/usr/bin/env python
# encoding: utf-8

import os, sys, glob, copy
import numpy as np

import datetime
import xarray as xr
import pandas as pd

from ..config import nawdex_dir
from .selector import  gather_simset, expname2conf_str, set_dateslices


'''
This is a package that collects data for different sets.
'''


######################################################################
######################################################################

def collect_sim_ave_cre4set( set_number, 
                             file_part = '',
                             file_format = 'default', 
                             allowed_set_range = [1,4] ):

    '''
    Collects average CRE data for a selected set.


    Parameters
    ----------
    set_number : int
       numeric identifier of a selected experiment set.

    file_format : str, optional, default = 'default'
       a string that defines file format, 
       restriction: two %s are needed at the moment

    allowed_set_range : list, optional, default = [1, 4]
       min & max of the allow set range

    
    Returns
    --------
    dset_sim : xarray Dataset
       set that contains time series of simulated CRE effects.

    '''

    if set_number < allowed_set_range[0] or set_number > allowed_set_range[1]:
        raise ValueError('set_number is outside allowed range')
    

    # get experiment list
    # ====================
    explist = gather_simset( set_number )
    date_slice = set_dateslices( set_number )


    if file_format == 'default':
        fformat = '%s/statistics/ave_cre%s-%s.nc' % ('%s', file_part, '%s')
    else:
        fformat = file_format % ('%s', file_part, '%s')


    # collect the CRE data 
    # ====================
    dlist = []
    for expname in explist:
        
        # open dataset
        fname = fformat % (nawdex_dir, expname)
        d = xr.open_dataset( fname )
        

        # this makes an expanded copy
        dex = d.expand_dims('idname', axis = -1)

        
        idname = expname2conf_str( expname )
        dex['expname'] = xr.DataArray([expname, ], dims='idname')
        dex['idname'] = [idname, ]
        
        dlist += [dex.copy(), ]
        
    dset_sim = xr.merge( dlist )

    return dset_sim.sel( time = date_slice )


######################################################################
######################################################################


def get_obs_cre4time_list( time, file_part ='-scaled', file_format = 'default'):


    '''
    Collects average CRE data for a selected set.


    Parameters
    ----------
    time : xarray time data
       list of time fow which obs CRE is input

    file_format : str, optional, default = 'default'
       a string that defines file format, 
       restriction: two %s are needed at the moment

    file_part : str, optional, default = '-scaled'
       selection of file part that specifies if bias correction of clearsky is used
       only used if `file_format == 'default'`

    
    Returns
    --------
    dset_obs : xarray Dataset
       set that contains time series of observed CRE effects.
    
    '''


    # make a list of time objects
    # ==============================
    timeobj_lists = []
    for t in sorted( time ):
        timeobj_lists += [ pd.Timestamp( t.data ).to_pydatetime() ,]

    timeobj_lists = np.array( timeobj_lists )



    if file_format == 'default':
        fformat = '%s/statistics/ave_cre%s-%s.nc' % ('%s', file_part, '%s')
    else:
        fformat = file_format % ('%s', file_part, '%s')




    # read daily stacks of obs data
    # ==============================
    t1, t2 = timeobj_lists.min(), timeobj_lists.max()

    t = copy.copy( t1 )

    dt = datetime.timedelta( days = 1 )
    obsdat = []

    while t <= t2: 
    
        # open dataset
        obsname = 'meteosat-nawdex-%s' % t.strftime('%Y%m%d')

        fname = fformat % (nawdex_dir, obsname)
        obsdat += [ xr.open_dataset( fname ), ]
        
        t += dt
    
    
    # merge and prepare dataset
    # =========================
    d = xr.merge( obsdat )
    dex = d.expand_dims( 'idname', axis = -1)

    expname = 'msevi%s' % file_part
    dex['expname'] = xr.DataArray([expname, ], dims='idname')
    dex['idname'] = [expname, ]
    
    
    return dex.sel( time = time )

######################################################################
######################################################################

def get_cre4set( set_number, allowed_set_range = [1,4], **kwargs ):


    '''
    Collects average CRE data for a selected set.


    Parameters
    ----------
    set_number : int
       numeric identifier of a selected experiment set.

    allowed_set_range : list, optional, default = [1, 4]
       min & max of the allow set range

    file_part : str, optional, default = '-scaled'
       selection of file part that specifies if bias correction of clearsky is used
       only used if `file_format == 'default`

    
    Returns
    --------
    dset : xarray Dataset
       set that contains time series of simulated and observed CRE effects.

    '''

    

    dset = get_stat4set( set_number, 
                         allowed_set_range = allowed_set_range, 
                         file_format = 'default', **kwargs)
                         
    return dset


######################################################################
######################################################################

def get_radflux4set( set_number, allowed_set_range = [1,4], **kwargs ):


    '''
    Collects average radiation flux data for a selected set.


    Parameters
    ----------
    set_number : int
       numeric identifier of a selected experiment set.

    allowed_set_range : list, optional, default = [1, 4]
       min & max of the allow set range

    
    Returns
    --------
    dset : xarray Dataset
       set that contains time series of simulated and observed CRE effects.

    '''

    
    file_format =  '%s/statistics/ave_radfluxes%s-%s.nc'

    dset = get_stat4set( set_number, 
                         allowed_set_range = allowed_set_range, 
                         file_format = file_format, **kwargs)
                         
    return dset


######################################################################
######################################################################

def get_stat4set( set_number, allowed_set_range = [1,4], file_format = 'default', method = 'all' ):


    '''
    Collects average CRE data for a selected set.


    Parameters
    ----------
    set_number : int
       numeric identifier of a selected experiment set.

    allowed_set_range : list, optional, default = [1, 4]
       min & max of the allow set range

    file_format : str, optional, default = 'default'
       a string that defines file format, 
       restriction: two %s are needed at the moment

    method : str, optional, default = 'all'
        selects if all data are input (`all`) 
        or if only data with no-nan clearsky are input (`strict`)
        

    
    Returns
    --------
    dset : xarray Dataset
       set that contains time series of simulated and observed CRE effects.

    '''

    # a small wrapper to get 'all' input inlcuded
    if set_number == 'all':

        set_range = list(range( allowed_set_range[0], allowed_set_range[1] + 1))

        dset = get_stat4all( set_range = set_range, file_format = file_format, method = method )

        return dset
    # --------------------------------------------------


    dlist = []

    # get simulated CRE
    # ====================
    dsim = collect_sim_ave_cre4set( set_number, 
                                    file_format = file_format,
                                    allowed_set_range = allowed_set_range )

    dlist +=[ dsim, ]
    
    # get the two observation variants
    # ========================================
    try: 
        dobs_scaled = get_obs_cre4time_list( dsim.time, 
                                             file_format = file_format,
                                             file_part ='-scaled')
        dlist += [ dobs_scaled, ]
    except:
        pass

    try:
        dobs_not_scaled = get_obs_cre4time_list( dsim.time, 
                                                 file_format = file_format,
                                                 file_part ='-not_scaled')
        dlist += [ dobs_not_scaled, ]
    except:
        pass


    return xr.merge( dlist )

######################################################################
######################################################################

def get_stat4all( set_range = list(range(1, 5)), file_format = 'default', method = 'all' ):
        
    '''
    Read and stack all input sets (CRE or Radiation Fluxes).
    
    
    Parameters
    ----------
    set_range : list, optional, default = range(1,5)
        list of set number to be input
        
    file_format : str, optional, default = 'default'
        file format defintion which is forwarded to the function 'get_stat4set`
        
    method : str, optional, default = 'all'
        selects if all data are input (`all`) 
        or if only data with no-nan clearsky are input (`strict`)
        
        
    Returns
    --------
    dset : xarray Dataset
        the dataset which contains average CRE or radfluxes
    '''
    
    dlist = []
    for iset in set_range:
        dlist += [get_stat4set( iset, file_format = file_format ), ]
    
    
    if method == 'all':
        # all data are stacked in time
        dset = xr.concat( dlist, dim = 'time' )
        
    elif method == 'strict':
        # only data if no nans in average clearsky are stacked
        
        # 1st stack all data
        dall = xr.concat( dlist, dim = 'time' )
    
        # 2nd contain included data
        dclear = dall.sel(ct = 'clear_ocean').dropna('idname')

        idnames = dclear.idname.data
        dset = dall.sel( idname = idnames )
        
    return dset

######################################################################
######################################################################
