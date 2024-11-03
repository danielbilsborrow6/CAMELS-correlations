import numpy as np
import h5py
import hdf5plugin
import pickle

def ellipticity(centre, theta, weight, x_y_or_z='z'):
    '''Calculates the ellipticity of a galaxy given its centre and positions of stellar particles
    centre - 3D position of Centre of galaxy
    theta - 3D position of stars
    x_y_or_z: from whcih axis do we want to calculate out 2D ellipticity
    weight - weighting of each star - defined as the density of space around that star'''
    xyz = {'x':[1,2], 'y':[2,0], 'z':[0,1]}
    perp_ax = xyz[x_y_or_z]
    centre = np.array([centre[perp_ax[0]], centre[perp_ax[1]]]).T       # 2D
    theta = np.array([theta[:,perp_ax[0]], theta[:,perp_ax[1]]]).T        # 2D
    separation = (theta - centre) %25 #calculating separations of members from cluster centre
    for i in range(separation.shape[0]):
        for j in range(2):  # Iterate over x, y, and z components
            if separation[i, j] < -10:
                separation[i, j] += 25
            elif separation[i, j] > 10:
                separation[i, j] -= 25
#     mag = np.linalg.norm(separation, axis=1)
#     separation = separation[mag<5] # filtering out stars which are more than 5 Mpc away from galaxy
#     weight = weight[mag<5]
    prob = weight/np.max(weight)
    prob = np.array([prob,prob]).T # multiply x and y coord
    separation_scaled = np.multiply(separation, prob)

    Q = (separation.T.dot(separation_scaled))         #'the correlation matrix'
    epsilon = (Q[0, 0] - Q[1, 1] + 2j*Q[0,1])/(Q[0, 0] + Q[1,1] + 2*np.sqrt(np.linalg.det(Q)))				#epsilon

    return epsilon


#filenum = 12
for filenum in [145,169,183,447,503,539,719,747,888,964]:
    # Importing snapshot and catalogue data at redshift z=0
    snapshot = f"../CAMELS/LH{filenum}_snap_033IllustrisTNG.hdf5"  # snapshot name
    # open the snapshot
    f = h5py.File(snapshot, 'r')
    pos_dm = f['PartType1/Coordinates'][:]/1e3  #positions of dark matter in Mpc/h
    pos_s = f['PartType4/Coordinates'][:]/1e3  # star positions in Mpc/h
    mass_s = f['PartType4/Masses'][:]*1e10  # star masses in Mpc/h
    # close file
    f.close()

    # catalogue name
    catalogue = f"../CAMELS/LH{filenum}_fof_subhalo_tab_033.hdf5"
    # open the catalogue
    f = h5py.File(catalogue, 'r')
    # looking to see data in cataloge
    # def print_dataset_name(name,g):
    #     print(name,'&',g)
    # f.visititems(print_dataset_name)
    pos_sh  = f['Subhalo/SubhaloPos'][:]/1e3     #positions of SUBFIND subhalos in Mpc/h
    subh_M_R_12 = f['Subhalo/SubhaloMassInRadType'][:,4]*1e10 # total stellar mass of twice the stellare alf-mass radius in Msun/h
    nstar_h = f['Group/GroupLenType'][:,4]            # total number of stars in each halo
    nstar_sh = f['Subhalo/SubhaloLenType'][:,4]            # total number of stars in each subhalo
    n_subhalos = f['Group/GroupNsubs'][:]             # number of subhalos in each halo
    # close file
    f.close()

    ############

    # Assigning every star to a subhalo according to SUBFIND algorithm
    # If a star does not belong to a subhalo but belongs to a halo, it does not get assigned an index. Stars which do not belong to any halo are at the end of the arrays thus do not get counted.
    assigned = np.zeros(len(pos_s), dtype=bool) # Initialize an array to keep track of assigned star particles
    # store the assignment of each star particle to a galaxy particle
    assignment = -np.ones(len(pos_s), dtype=int)  # The index of the galaxy particle, for unassigned stars assignment =-1

    begin_slice = 0
    end_slice = nstar_sh[0] # end_slice - begin_silice = number of stars assigned to this subhalo w index subhalo_index
    star_count = 0 # star index we are at
    subhalo_index = 0   # subhalo index we are at

    for i, number_sh in enumerate(n_subhalos): 
        if number_sh!=0: 
            for j in range(number_sh):          # looping through every subhalo in a halo

                assigned[begin_slice:end_slice] = True
                assignment[begin_slice:end_slice] = subhalo_index

                if nstar_sh[subhalo_index]!=0:
                    begin_slice=end_slice
                    end_slice = begin_slice + nstar_sh[subhalo_index+1]

                star_count += nstar_sh[subhalo_index]

                subhalo_index +=1



            old_star_count = star_count
            star_count = np.sum(nstar_h[:i+1])
            #print("unasigned stars: ", star_count - old_star_count)
            begin_slice = star_count   # skipping the stars with no subhalo
            if subhalo_index!=len(nstar_sh):
                end_slice = star_count+nstar_sh[subhalo_index]
        else:
            continue
    #print("It is",np.sum(n_subhalos)==subhalo_index, "we have counted all subhalos.")

    #############

    #### Galaxies are subhalos with Mstar > 1e8 Msun
    min_MstarMass = 1e8 # threshold stellar mass approximatley 10 stellar particles

    # removing unasigned stars from star index
    pos_s1 = pos_s[assigned]
    mass_s1 = mass_s[assigned]
    assignment1 = assignment[assigned]
    # replacing subhalos with low stellar mass with np.nan
    pos_g = pos_sh
    pos_g[subh_M_R_12<min_MstarMass] = np.nan
    pos_g2 = pos_g[~np.isnan(pos_g).any(axis=1)] # sifting 
    nstar_g = nstar_sh.astype(float)
    nstar_g[subh_M_R_12<min_MstarMass] = np.nan
    #print('Galaxy positions shape: ', pos_g.shape)

    high_mass = np.where((subh_M_R_12>min_MstarMass) & (nstar_sh > 10))[0]
    #print(high_mass.shape, "galaxies")

    # Create a boolean mask for the stars above the threshold mass
    mask = np.isin(assignment1, high_mass)

    # Filter out stars in subhalos below the threshold mass
    pos_s2 = pos_s1[mask]
    mass_s2 = mass_s1[mask]
    filtered_assignment1 = assignment1[mask]
    #print("number of stars remaining:",filtered_assignment1.shape)


    ################


    e_glxys = {} # dictionary for ellipticities 
    assigned2 = np.zeros(len(pos_g), dtype=bool)
    for axis in ['x','y','z']:
        e_glxys[axis] = 3.0*np.ones(len(pos_g), dtype = 'complex_') # set non calaculated values to 3

    for axis in ['x','y','z']:
        for i in range(len(pos_g)):
            if ~np.isnan(nstar_g[i]):
                #print(i,len(mass_s2[filtered_assignment1==i]), pos_s2[filtered_assignment1==i].shape,"{:.3E}".format(subh_M_R_12[i]))
                if len(mass_s2[filtered_assignment1==i])>0: # some galaxies have no stars assigned to them ?
                    assigned2[i]=True
                    e_glxys[axis][i] = ellipticity(centre=pos_g[i], theta=pos_s2[filtered_assignment1==i],
                                                   weight=mass_s2[filtered_assignment1==i], x_y_or_z=axis)


    for axis, ell_array in e_glxys.items():
        e_glxys[axis] = ell_array[ell_array!=3]
        #print(f"Old Shape of angles and ratios for axis '{axis}': {e_glxys[axis].shape}")

    pos_g3 = pos_g[assigned2] # one last filtering for galaxies which have no assigning stars
    #################

    # Save dictionaries to a file using pickle
    with open(f'../CAMELS/ellipticity_measurements/LH{filenum}_ellipticities.pkl', 'wb') as f:
        pickle.dump({
            'posg': pos_g3,
            'ellipticities': e_glxys,
            'dm_den': pos_dm
        }, f)
        
        
        
    print("Done file:", filenum,"Num galaxies:",len(pos_g3))
    
    
    
    
    
    
    
    

