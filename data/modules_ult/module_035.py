def local_computecov(start_list, end_list, local_entry):
        ret_cov = 0
        Ls = local_entry[0]
        Le = local_entry[1]
        for Ts, Te in zip(start_list, end_list):
            if Ls > Ts and Ls < Te and Le > Ts and Le < Te:
                # in
                ret_cov += Le - Ls
            if Ls < Ts and Ls < Te and Le > Ts and Le < Te:
                # start out
                ret_cov += Le - Ts
            if Ls > Ts and Ls < Te and Le > Ts and Le > Te:
                # end out
                ret_cov += Te - Ls
            if Ls < Ts and Ls < Te and Le > Ts and Le > Te:
                # start&end out
                ret_cov += Te - Ts
        return (ret_cov)
