def get_bbr_passw(db_name):
    if db_name in {'PSB', 'PSBE', 'PSBF', }:
        return "super"
    elif db_name in {'TNA01', 'TNAM01', 'TDB7', 'TSF8', 'TDB8', 'TDB1', 'TSF3', 'TSE1', 'PSBPP',
                     'PSBEPP',
                     'PSBFPP', 'PSBIFT', 'PSBFIFT', 'TSE9', 'TSF9', 'TDB9', 'SVPSB', 'SVPSBE',
                     'SVPSBF',
                     'TSE02', 'TSF02', 'TDB02', 'RNA01', 'INA02'}:
        return "repus"
    elif db_name in {'PSB', 'PSBE', 'PSBF', }:
        return "14zXm+47"
    else:
        return None


def get_supervisor_workplace(db_name):
    group_wp_psbe = {'PSBE', 'TSE1', 'PSBEPP', 'PSBEIFT', 'TSE9', 'SVPSBE', 'TSE02', 'LTPSBE', 'RNAE01',
                     'TNAE01', 'INAE02'}
    group_wp_psbf = {'PSBF', 'TSF8', 'TSF3', 'PSBFPP', 'PSBFIFT', 'TSF9', 'SVPSBF', 'TSF02', 'LTPSBF',
                     'RNAF01', 'TNAF01', 'INAF02'}
    group_wp_psb = {'PSB', 'TDB7', 'TDB8', 'TDB1', 'PSBPP', 'PSBIFT', 'TDB9', 'SVPSB', 'TDB02', 'LTPSB',
                    'RNA01', 'INA02'}
    if db_name in group_wp_psbe:
        return 'PSBE'
    elif db_name in group_wp_psbf:
        return 'PSBF'
    elif db_name in group_wp_psb:
        return 'PSB'


def get_passw(schema_name, base_name):
    if str(schema_name).upper() == "ACR":
        if str(base_name).upper() in {'TDB7', 'TDB1', 'TDB8', 'TDB9', 'TSF3', 'TSF8', 'TSF9', 'TSE1', 'TSE9', 'PSBPP',
                                      'PSBEPP', 'PSBFPP', 'PSBIFT', 'PSBEIFT', 'PSBFIFT', 'TPSBFCT', 'TFACT', 'TSKHED',
                                      'LTPSB', 'LTPSBE', 'LTPSBF', 'RNA01', 'RNAE01', 'RNAF01', 'INA02', 'INAE02',
                                      'INAF02', 'TNA01', 'TNAE01', 'TNAF01', 'RFACT01', 'TFACT01', 'TNAM01'}:
            return "acr"
        elif str(base_name).upper() in {'PSB', 'PSBE', 'PSBF', 'PSBM'}:
            return "QAzXSW#9"
        else:
            return None
    elif str(schema_name).upper() == "SYS_FX":
        if str(base_name).upper() == "PSB":
            return "crotyk73flav"
        elif str(base_name).upper() in {'TDB7', 'TDB1', 'TDB8', 'TDB9', 'TSF3', 'TSF8', 'TSF9', 'TSE1', 'TSE9', 'TSE9',
                                        'TPSBFCT', 'CYP1A', 'TFACT', 'TSKHED', 'PSBIFT', 'PSBEIFT', 'PSBFIFT', 'LTPSB',
                                        'LTPSBE', 'LTPSBF'}:
            return "sys_fx"
    elif str(schema_name).upper() == "OD":
        if str(base_name).upper() in {'PSB', 'PSBE', 'PSBF', 'PSBM', 'PSBFCT', 'CYP1', 'PSBFACT'}:
            return "phuzas27chet"
        elif str(base_name).upper() == "SKHED":
            return "oracle2014sys"
        elif str(base_name).upper() in {'PSBPP', 'PSBEPP', 'PSBFPP', 'PSBIFT', 'PSBFIFT', 'CYP1A', 'TDB7', 'TDB1',
                                        'TDB8', 'TDB9', 'TSF3', 'TSF8', 'TSF9', 'TSE1', 'TSE9', 'TPSBFCT', 'PSBFACT',
                                        'DFACT', 'RFCT01', 'TFACT', 'TFACT9', 'TSKHED', 'DSKHED', 'SVPSB', 'SVPSBE',
                                        'SVPSBF', 'LTPSB', 'LTPSBE', 'LTPSBF', 'TDB02', 'TSE02', 'TSF02', 'RNA01',
                                        'RNAE01', 'RNAF01', 'TNA01', 'TNAE01', 'TNAF01', 'RFACT01', 'TFACT01',
                                        'TNAM01'}:
            return "od456"
    elif str(schema_name).upper() == "BBR":
        if str(base_name).upper() in {'PSB', 'SKHED', 'DSKHED', 'TSKHED'}:
            return "bbr"
        elif str(base_name).upper() in {'PSBE', 'PSBF', 'PSBM'}:
            return "1q2w3e"
        elif str(base_name).upper() in {'PSBPP', 'PSBEPP', 'PSBEPP', 'PSBEPP', 'PSBFPP', 'PSBFCT', 'CYP1', 'CYP1A',
                                        'TDB7', 'TDB1', 'TSF3', 'TSF8', 'TSF9', 'TSE1', 'TSE9', 'TPSBFCT', 'PSBFACT',
                                        'DFACT', 'TFACT', 'SVPSB', 'SVPSBE', 'SVPSBF', 'LTPSB', 'LTPSBE', 'LTPSBF',
                                        'PSBIFT', 'PSBEIFT', 'PSBFIFT', 'TDB02', 'TSE02', 'TSF02', 'RNA01', 'RNAE01',
                                        'RNAF01', 'INA02', 'INAE02', 'INAF02', 'TNA01', 'TNAE01', 'TNAF01', 'RFACT01',
                                        'TFACT01', 'TNAM01'}:
            return "od456"
    elif str(schema_name).upper() == 'SUPER':
        if str(base_name).upper() in {'PSBM', 'SVPSBE', 'SVPSBF', 'LTPSB', 'LTPSBE', 'LTPSBF', 'RNAE01', 'RNAF01',
                                      'INAE02',
                                      'INAF02', 'TNAE01', 'TNAF01'}:
            return "super"
        elif str(base_name).upper() in {'PSB', 'PSBE', 'PSBF', 'LTPSBE'}:
            return "14zXm+47"
        elif str(base_name).upper() in {'PSBPP', 'PSBEPP', 'PSBFPP', 'TDB7', 'TDB1', 'TDB9', 'TSF3', 'TSF9', 'TSE1',
                                        'TSE9',
                                        'SVPSB', 'PSBIFT', 'PSBEIFT', 'PSBFIFT', 'TDB02', 'TSE02', 'TSF02', 'RNA01',
                                        'INA02',
                                        'TNA01', 'TNAM01'}:
            return "repus"
        elif str(base_name).upper() in {'CYP1', 'CYP1A', 'TDB8', 'TSF8', 'PSBFCT', 'TPSBFCT', 'PSBFACT', 'DFACT',
                                        'TFACT',
                                        'RFACT01', 'TFACT01', 'SKHED', 'TSKHED', 'DSKHED'}:
            return "unknown"
    elif str(schema_name).upper() == "FACT":
        if str(base_name).upper() in {'PSBFACT', 'PSBFCT'}:
            return "vkmr56ivm8"
        elif str(base_name).upper() in {'TFACT','TPSBFCT'}:
            return "sz1164579"
        elif str(base_name).upper() == 'DFACT':
            return "fact"
    elif str(schema_name).upper()=="ICBXI":
        if str(base_name).upper() == 'PSBFACT':
            return "cliP9568yID472ui"
    elif str(schema_name).upper() == "DAEMON":
        if str(base_name).upper() in {'PSB','PSBE','PSBF'}:
            return "Cbkmysq$Dtnthyfkeyt1208"
        elif str(base_name).upper() in {'PSBFCT','CYP1','CYP1A','SKHED','TDB7','TDB4','TSE1','TSE2','TSE9','TSF3','TSF8','TSF9','TPSBFCT','DFACT', 'TFACT','PSBFACT', 'TSKHED','DSKHED','RNA01','RNAE01','RNAF01','INA02','INAE02','INAF02', 'TNA01','TNAE01','TNAF01','RFACT01','TFACT01','TNAM01'}:
            return "daemon"

