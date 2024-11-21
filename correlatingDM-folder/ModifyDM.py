from concurrent.futures import ProcessPoolExecutor
import h5py
import numpy as np
from astropy.io import fits

# Function to convert Cartesian coordinates to spherical coordinates
def cart_to_spherical(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    # make it so z is parallel to line of sight of observer
    theta = np.arccos(x / r)
    phi = np.arctan2(y, z)
    return r, theta, phi

# Function to convert spherical coordinates to RA and DEC in degrees
def spherical_to_ra_dec(theta, phi):
    ra = np.degrees(phi)
    dec = 90 - np.degrees(theta)
    return ra, dec




# Task function for parallel execution
def process_file(filenum):
    axis = 2  # [x,y,z]
    xyz = [[1, 2], [2, 0], [0, 1]]
    perp_ax = xyz[axis]

    # File paths
    DMcoord_path = f"/Volumes/CAMELSDrive/DM_Posns/LH{filenum}_coordinates.hdf5"
    output_path = f'/Volumes/CAMELSDrive/DM_pipelineInputs_z/CAMELS_DMRADEC_data_LH{filenum}.fits'
    rand_output_path = f'/Volumes/CAMELSDrive/DM_pipelineInputs_z/CAMELS_DMRADEC_rand_LH{filenum}.fits'

    with h5py.File(DMcoord_path, 'r') as f:
        pos_dm = f['PartType1/Coordinates'][:]
        
        
    ##### SAMPLING
    num_samples = pos_dm.shape[0] // 100

    sample_indices = np.random.choice(pos_dm.shape[0], size=num_samples, replace=False)
    samp_pos_dm = pos_dm[sample_indices]
    pos_dm=samp_pos_dm

    pos_dm[:, axis] += 10000
    r, theta, phi = cart_to_spherical(pos_dm[:, perp_ax[0]], pos_dm[:, perp_ax[1]], pos_dm[:, axis])
    ra, dec = spherical_to_ra_dec(theta, phi)

    # Save data FITS file
    data = fits.BinTableHDU.from_columns([
        fits.Column(name='RA', format='D', array=ra),
        fits.Column(name='DEC', format='D', array=dec),
        fits.Column(name='r_col', format='D', array=r)
    ])
    hdul = fits.HDUList([fits.PrimaryHDU(), data])
    hdul.writeto(output_path, overwrite=True)

    # Generate random data
    length = len(pos_dm[:, 0])
    ra_rand = np.random.uniform(min(ra), max(ra), length)
    dec_rand = np.random.uniform(min(dec), max(dec), length)
    r_rand = np.random.uniform(min(r), max(r), length)

    # Save random FITS file
    rand_data = fits.BinTableHDU.from_columns([
        fits.Column(name='RA', format='D', array=ra_rand),
        fits.Column(name='DEC', format='D', array=dec_rand),
        fits.Column(name='r_col', format='D', array=r_rand)
    ])
    rand_hdul = fits.HDUList([fits.PrimaryHDU(), rand_data])
    rand_hdul.writeto(rand_output_path, overwrite=True)
    
    print(f'converted{filenum}')



if __name__ == "__main__":
    filenums = range(0, 1000)
    with ProcessPoolExecutor(max_workers=4) as executor:
        executor.map(process_file, filenums)
