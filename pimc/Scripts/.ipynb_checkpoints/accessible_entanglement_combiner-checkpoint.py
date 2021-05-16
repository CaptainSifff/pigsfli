# Takes average <S2> from many random seeds
# and combines them into one file

# What we're doing on one file:
# 1) Loading P(n) for desired swapped sector mA
# 2) Load SWAP(n) files
# 3) Taking column sum for P(n) file for desired mA 
# 4) Taking column sum for SWAP(n) file
# 5) Dividing column sums of P(n) over column sums of SWAP(n)
# 6) Taking negative log of above result
# 7) Taking the average over seeds of above results
# 8) Take the standard error of above average

import os
import numpy as np

# Set values of U sweep
# U_list = np.round(np.geomspace(0.01,100,20),4)
U_list = np.array([3.3])
# U_list = np.array([0.500000,
# 0.730000,
# 1.065800,
# 1.556100, 
# 2.272000, 
# 3.300000, 
# 4.843100, 
# 7.071100,   
# 10.323900,
# 16.666667, 
# 22.007100, 
# 32.130800,
# 46.911700,
# 68.492100,
# 100.000000])

beta_list = [0.6,0.7,0.8,0.9,1.0,1.15,1.30,1.50,
             1.75,2.0,2.25,2.50,2.75,3.0,3.25,
             3.50,3.75,4.0,5.0,6.0]
beta_list = [0.6,0.7,0.8,0.9,1.0,1.15,1.30,1.50,
             1.75,2.0,2.5,3.0,3.5,
             4.0,4.5,5.0,5.5,6.0]
# beta_list = [0.6,0.7,0.8,0.9,1.0,1.15,1.30,1.50,
#              1.75,2.0,3.0,4.0]
# beta_list = [7.0]
S2_plot = []
S2_err_plot = []
for U in U_list:
    for beta in beta_list:
        for l_sector_wanted in [4]:
        
            incomplete_seeds = [] 
            seeds_list = list(range(1000))
            seeds_measured = []

            # Set desired parameters of calculation
            L = "%d"%(2*l_sector_wanted)
            N = "%d"%(2*l_sector_wanted)
            l_max = "%d"%l_sector_wanted
            beta = "%.6f"%beta
            bin_size = "10000"
            bins_wanted = "1000"
            D = "1"
            U = "%.6f"%(U)
            t = "1.000000"

            # Get path where raw data for the simulation is stored
            path = D+"D_"+L+"_"+N+"_"+l_max+"_"+U+"_"+\
                   t+"_"+beta+"_"+bin_size+"_"+bins_wanted+"/"
            path = "/Users/ecasiano/Desktop/Data/"+path

            # Stores all files in the directory
            filenames_all = os.listdir(path)

            # Set size of subregion A we want to calculate (mA=l^D)
    #         l_sector_wanted = int(L)//2
    #         l_sector_wanted = 4

            # Convert strings back to numbers
            L = int(L)
            N = int(N)
            l_max = int(l_max)
            beta = float(beta)
            bin_size = int(bin_size)
            bins_wanted = int(bins_wanted)
            D = int(D)
            U = float(U)
            t = float(t)

            # Saves the files relevant to P(n) & S2(n) calculation
            files_PnSquared = []
            files_SWAPn = []
            files_Pn = []

            # Iterate over all filenames in path
            for filename in filenames_all:

                # Extract parameter information from file name
                parameters = filename.split("_")

                if parameters[0]=='1D' or parameters[0]=='2D' or parameters[0]=='3D':

                    D_want = int((parameters[0])[0]) # hypercube dimension
                    L_want = int(parameters[1]) # hypercube linear size
                    N_want = int(parameters[2]) # total particles
                    l_want = int(parameters[3]) # subsystem linear size (actually l_max)
                    U_want = float(parameters[4]) # interaction potential
                    t_want = float(parameters[5]) # tunneling parameter
                    beta_want = float(parameters[6]) # imaginary time length (K_B*T)**(-1)
                    bin_size_want = int(parameters[7])
                    bins_want = int(parameters[8]) # number of bins saved in file
                    filetype = (parameters[9]).split("-mA") # identifies the data stored in file
                    seed = int(parameters[10].split(".")[0]) # random seed used

                    if filetype[0]=='PnSquared' and int(filetype[1])==l_sector_wanted:
                        # Set parameters of simulations from different seeds we want to evaluate [D,L,N,l,U,t,beta,bins,type]
                        parameters_to_evaluate = [D_want,
                                                  L_want,
                                                  N_want,
                                                  l_want,
                                                  U_want,
                                                  t_want,
                                                  beta_want,
                                                  bin_size_want,
                                                  bins_want,
                                                  'PnSquared']

                        if [D,L,N,l_max,U,t,beta,bin_size,bins_wanted,filetype[0]] == parameters_to_evaluate:
                            if os.stat(path+filename).st_size > 0:
                                with open(path+filename) as f:
                                   count = sum(1 for _ in f)
                                if count == bins_wanted: # only consider files that managed to save number of bins wanted
                                    files_PnSquared.append(filename)

                                    filename_splitted = filename.split('_')
                                    filename_splitted[9] = 'Pn-mA'+str(l_sector_wanted)
                                    filename_Pn = "_".join(filename_splitted)
                                    files_Pn.append(filename_Pn)

                                    filename_splitted = filename.split('_')
                                    filename_splitted[9] = 'SWAPn-mA'+str(l_sector_wanted)
                                    filename_SWAPn = "_".join(filename_splitted)
                                    files_SWAPn.append(filename_SWAPn)

                                    seeds_measured.append(seed)

                                else: 
                                    incomplete_seeds.append(seed)

            # Get total number of seeds 
            number_of_seeds = len(files_PnSquared)//1

            print("\nN: ",N)
            print("L: ",L)
            print("partition size: ", l_sector_wanted)
            print("U: ",U)
            print("beta: ",beta)

            # Get column sum of P(n) files for each seed
            print('\nInitial number of seeds: ',number_of_seeds)
            PnSquared_col_sums = np.zeros((number_of_seeds,N+1)).astype(int)
            Pn_col_sums = np.zeros((number_of_seeds,N+1)).astype(int)
            SWAPn_col_sums = np.zeros((number_of_seeds,N+1)).astype(int)
            for s in range(number_of_seeds):

                data = np.loadtxt(path+files_PnSquared[s])
                PnSquared_col_sums[s] = np.sum(data,axis=0)

                data = np.loadtxt(path+files_Pn[s])
                Pn_col_sums[s] = np.sum(data,axis=0)

                data = np.loadtxt(path+files_SWAPn[s])
                SWAPn_col_sums[s] = np.sum(data,axis=0)

            # Jacknife 
            SWAPn_col_seed_sum = np.sum(SWAPn_col_sums,axis=0) # shape: (1,N+1)... I think
            PnSquared_col_seed_sum = np.sum(PnSquared_col_sums,axis=0)
            Pn_col_seed_sum = np.sum(Pn_col_sums,axis=0)

            S2n_jacknifed = np.zeros(SWAPn_col_sums.shape)
            S2acc_jacknifed = np.zeros(SWAPn_col_sums.shape[0]) # one element for each seed
            Pn_jacknifed = np.zeros(Pn_col_sums.shape)
            ratio_jacknifed = np.zeros(SWAPn_col_sums.shape)
            for i in range(SWAPn_col_sums.shape[0]):

                # Generate jacknifed data
                SWAPn_jacknifed_sum = SWAPn_col_seed_sum - SWAPn_col_sums[i]
                PnSquared_jacknifed_sum = PnSquared_col_seed_sum - PnSquared_col_sums[i]
                Pn_jacknifed_sum = Pn_col_seed_sum - Pn_col_sums[i]

                # n-resolved Renyi Entropy for data point i
                ratio_jacknifed[i] = SWAPn_jacknifed_sum / PnSquared_jacknifed_sum
                S2n_jacknifed[i] = -np.log ( ratio_jacknifed[i] ) 

                # Grab indices of n-sectors where S2acc will not be NaN or inf.
                good_nsectors = np.argwhere(np.logical_not(np.isnan(ratio_jacknifed[i])) & np.logical_not(np.isinf(ratio_jacknifed[i])))

                # Accessible Renyi Entropy for data point i
    #             S2acc_jacknifed[i] = np.sum(Pn_jacknifed_sum * S2n_jacknifed[i]) / np.sum(Pn_jacknifed_sum)
                S2acc_jacknifed[i] = -2*np.log(np.sum(Pn_jacknifed_sum[good_nsectors] * np.sqrt(ratio_jacknifed[i][good_nsectors])) / np.sum(Pn_jacknifed_sum[good_nsectors]))

                # Local particle number distribution for data poin i
                Pn_jacknifed[i] = Pn_jacknifed_sum / np.sum(Pn_jacknifed_sum)

            print("Final number of seeds: ",number_of_seeds,"\n")     

            # Calculate Renyi Entropies of each local particle number sector
            S2n_mean = np.mean(S2n_jacknifed,axis=0)
            S2n_err = np.std(S2n_jacknifed,axis=0) * np.sqrt(S2n_jacknifed.shape[0])

            # Calculate the total accessible entanglement entropy. Old way. MIGHT need error propagation and sum up all sectors instead.
            S2acc_mean = np.mean(S2acc_jacknifed,axis=0)
            S2acc_err = np.std(S2acc_jacknifed,axis=0) * np.sqrt(S2acc_jacknifed.shape[0])

            # Get mean of Pn and std errors
            Pn_mean = np.mean(Pn_jacknifed,axis=0)
            Pn_err = np.std(Pn_jacknifed,axis=0) * np.sqrt(number_of_seeds)

            # Print P(n),S2(n) for each sector to screen
            for i in range(len(S2n_mean)):
                print("P(n=%d) = %.4f +/- %.4f"%(i,Pn_mean[i],Pn_err[i]))
            print("\n")
            for i in range(len(S2n_mean)):
                print("S2(n=%d) = %.4f +/- %.4f"%(i,S2n_mean[i],S2n_err[i]))

            print("\nS2acc = %.4f +/- %.4f \n"%(S2acc_mean,S2acc_err))
            
            S2_plot.append(S2acc_mean)
            S2_err_plot.append(S2acc_err)

            # Check that throwaway error is smaller than standard error
            bad_nsectors = np.argwhere(np.isnan(S2acc_mean))
            throwaway_err = np.sum(Pn_mean[bad_nsectors])
            if (throwaway_err/S2acc_err > 0.1):
                print("WARNING: Throwaway error larger than 10% of the standard error")
                print("Throwaway Error: ",throwaway_err)
                print("S2acc_err: ",S2acc_err)
                

        # print("Seeds not included for some reason: ")

        # for i in seeds_list:
        #     if not(i in seeds_measured):
        #         print(i,end=",")
        
print("<S2Acc>=",S2_plot)
print("S2Acc_err=",S2_err_plot)
print("beta=",beta_list)