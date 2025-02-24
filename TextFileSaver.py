import os
import set_passw


def generate_add_sql(sorted_list, version, db_name):
    """ на вход подается список задач со списком обьектов, каждый обьект имеет список атрибутов [путь к файлу, автор изменения,номер коммита]"""

    header = fr"""
spool d:\svn\log_\{version}\{version}_{db_name}.log
set serveroutput on 


whenever sqlerror continue
prompt настройка триггера  DDL и DisableSpravSync
begin
registry.SetValue('PSB\COMMON\DDL_TRIGGER', null, '0');
commit;
end;
/
begin
registry.SetValue('\PSB\MDM\DisableSpravSync', null, '1');
commit;
end;
/

begin
execute immediate 'alter session set plsql_debug=false plsql_optimize_level=2';
end;
/

declare
v_cnt number;
begin
select count(*) into v_cnt from scriptpatch where SCRIPTNAME = 'psb_ver';
if v_cnt = 0 then
insert into scriptpatch (SCRIPTNAME, PATCHNAME, PATCHDATE) values ('psb_ver', '0', sysdate);
commit;
end if;
insert into scriptpatch (SCRIPTNAME, PATCHNAME, PATCHDATE) values ('psb_ver', '{version}', sysdate);
commit;
end;
/

prompt Лукашина, стоп очередей
set serveroutput on
declare
name varchar2(14);
begin
select name into name from v$database ;
case 
      when  name in ('TSE15','TSF16') then dbms_output.put_line('Не останавливаем для: '||name);
      else od.psb_cp_cashpooling.OnLineCP_StopDequeue;
     end case;
end;
/

--exec psb_cross_pkg.setPatchBank
alter trigger T_tableauditlog enable;
commit;

select sch.OWNER, NVL(a.cnt,0) cnt
from ( select  OWNER, COUNT(*) AS CNT
from all_objects where 
status = 'INVALID' AND 
OWNER IN ('BBR','FACT','NAQ','OD','AFW$','DHW$','IMP$')
GROUP BY OWNER) a, ( select 'BBR' as OWNER from dual
union  select 'FACT' as OWNER from dual
union  select 'DHW$' as OWNER from dual
union  select 'IMP$' as OWNER from dual
union  select 'NAQ' as OWNER from dual
union  select 'AFW$' as OWNER from dual
union  select 'OD' as OWNER from dual) sch
where A.OWNER (+) = sch.owner and cnt <> 0 ORDER BY 1
/"""
    head1 = f"""
prompt переconnect  ===== ЗАДАЧА  task_number; === база {db_name};;
connect od/{set_passw.get_passw('od',db_name)}@{db_name}
"""
    head2 = """

alter session set ddl_lock_timeout=150; 
--exec od.psb_cross_pkg.setPatchBank
begin
execute immediate 'alter session set plsql_debug=false plsql_optimize_level=2';
end;
/
"""

    body = []
    for task in sorted_list:
        task_number = task[0]
        body.append(f"prompt ===== Задача {task_number}; ========= база {db_name};")
        for obj in task[2:]:
            obj_path = obj[6]
            author = obj[2]
            commit = obj[1]
            data = obj[3]
            body.append(f"@comp {obj_path}    --#{task_number}     {author}     {commit}   {data}")

    footer = r"""
exec psb_cross_pkg.resetPatchFlag
-------




alter trigger T_tableauditlog disable;
/

prompt включение триггера проверки изменения DDL
begin
registry.SetValue('PSB\COMMON\DDL_TRIGGER', null, '1');
commit;
end;
/
begin
registry.SetValue('\PSB\MDM\DisableSpravSync', null, '0');
commit;
end;
/



prompt Лукашина, старт очередей
set serveroutput on
declare
name varchar2(14);
begin
select name into name from v$database ;
case 
      when  name in ('TSE15','TSF16') then dbms_output.put_line('Не останавливаем для: '||name);
      else od.psb_cp_cashpooling.OnLineCP_StartDequeue;
     end case;
end;
/

declare
encdng varchar2(20);
begin
--см сюда, если новая кодировка http://dba.stackexchange.com/questions/11531/is-there-any-doc-listing-standard-oracle-character-sets-correspondencies
SELECT value into encdng FROM NLS_DATABASE_PARAMETERS where parameter = 'NLS_CHARACTERSET';
case encdng
 when  'CL8MSWIN1251' then encdng := 'Windows-1251';
 when 'CL8ISO8859P5' then encdng := 'ISO-8859-5';
 else encdng := null; --неизвестная оставляем на усм пакета и надеемся на лучшее
end case;
sys.utl_mail.send('ОУРиС <noreply@psbank.ru>', 'ovpo_na@psbank.ru', null, null, 'Произошло обновление тестовой среды.', 'Обратите внимание,  на тестовой базе указанной ниже обновлен ряд объектов, из задач:  <br><br> ,NA-99703,NA-99606,NA-99763 <br><br>Базы: INA02 <br><br>Devops: suslikovvv', 'text/html; charset='||encdng, 1);

end;
/



spool off
exit;

"""
    return header + head1+head2+"\n".join((body)) + footer


def generate_text_comp_sql():
    text = r"""
    set verify off
    set pagesize 0
    set serveroutput on size unlim
    set feedback off
    set define on
    set sqlblanklines on
    commit;
    select ' '||TO_CHAR(SYSDATE,  'DD/mm/YYYY HH24:MI:SS')||'  ' from dual;
    set feedback on
    prompt .       .       .       .       .       .       .       .       . Start: &1  Rev. &4
    @&1
    show errors
    set define on
    prompt .       .       .       .       .       .       .       .       .   End: &1
    set feedback off
    set feedback on
    commit;

    select sch.OWNER, NVL(a.cnt,0) cnt
    from ( select  OWNER, COUNT(*) AS CNT
    from all_objects where 
    status = 'INVALID' AND 
    OWNER IN ('BBR','FACT','NAQ','OD','AFW$','DHW$','IMP$')
    GROUP BY OWNER) a, ( select 'BBR' as OWNER from dual
    union  select 'FACT' as OWNER from dual
    union  select 'DHW$' as OWNER from dual
    union  select 'IMP$' as OWNER from dual
    union  select 'NAQ' as OWNER from dual
    union  select 'AFW$' as OWNER from dual
    union  select 'OD' as OWNER from dual) sch
    where A.OWNER (+) = sch.owner and cnt <> 0 ORDER BY 1
    /
    prompt  
    prompt  
    """
    return text


def generate_text_recompile_sql():
    text = r"""
    exec psb_cross_pkg.resetPatchFlag

    begin
    compileall();
    end;
    /
    exit;
    """
    return text


def generate_text_s_bat():
    text = r"""@echo off
    set CUR_DATE=%DATE%
    set CURDATE=%TIME%

    md D:\ARCHIVE_LOG

    svn up d:\svn\_log_\for_commit\assembler_logs\ --accept=theirs-full

    copy /Y %1 "%D:\ARCHIVE_LOG\%~n1__%CUR_DATE:~0,2%_%CUR_DATE:~3,2%_%CUR_DATE:~6,4%__%CURDATE:~0,2%h%CURDATE:~3,2%min_%2@%3%.log"
    copy /Y %1 "%d:\svn\_log_\for_commit\assembler_logs\%~n1__%CUR_DATE:~0,2%_%CUR_DATE:~3,2%_%CUR_DATE:~6,4%_%2@%3%.log"

    del /f  d:\svn\_log_\for_commit\assembler_logs\%3.log

    rename d:\svn\_log_\for_commit\assembler_logs\%~n1__%CUR_DATE:~0,2%_%CUR_DATE:~3,2%_%CUR_DATE:~6,4%_%2@%3.log  %3.log

    svn add d:\svn\_log_\for_commit\assembler_logs\*.*
    svn propset LikeRobotsDo 10_01_2023_17-42 d:\svn\_log_\for_commit\assembler_logs\%3.log
    svn ci d:\svn\_log_\for_commit\assembler_logs\ -m "Version:{self.BUILD_VERSION} | date:{datetime.datetime.now().strftime("%d_%m_%Y_%H-%M")}"

    python log_commit.py %3.log

    pause
    exit
    """
    return text


def generate_text_check_rev_bat():
    text = """echo CHECKING REVISION - %2

python check_rev.py %1 

exit"""
    return text


def generate_text_check_rev_py():
    text = r"""# -*- coding: cp1251 -*-
import re
import sys

path_to_folder_build = sys.argv[1]


dict_name_rev = {}
rev = 'rev'
num_line = 'num_line'

#Читаем содержимое полностью
with open(f'{path_to_folder_build}', 'r') as full_file_build:
    old_data_full = full_file_build.read()
number_line = -1
result = ''

with open(f'{path_to_folder_build}', 'r') as file_build:
    #Читаем построчно
    old_data_lines = file_build.readlines()
    #Заходим в каждую строку
    for line in old_data_lines:
        #Фиксируем текущий номер строки
        number_line += 1
        #Работаем с теми, которые начинаются с @comp
        if line.startswith('@comp'):
            #Имя объекта
            name_obj = line.split()[1].split('\\')[-1]
            #Ревизия текущая
            revision_old = line.split()[4].rstrip(';')
            reg = fr'\\{name_obj}'
            #Ищем имена объектов ,которые повторяются более 1 раза
            if len(re.findall(reg, old_data_full)) > 1:
                #Формируем словарь - имя объекта, его ревизии и номера строк этих объектов
                if name_obj in dict_name_rev.keys():
                    dict_name_rev[name_obj].append([{rev: revision_old}, {num_line: number_line}])
                else:
                    dict_name_rev[name_obj] = [[{rev: revision_old}, {num_line: number_line}]]
    #Работаем с полученным словарем, берем каждое имя объекта
    for names in dict_name_rev:
        #Временный список ревизий по объекту, для поиска максимальной
        tmp_rev = []
        #Список младших ревизий, к которым нужно добавить PARENT
        rev_for_upd = []
        #Заходим в значение ключа по имени объекта
        for rev_num in dict_name_rev[names]:
            #Заполняем временный список, для поиска максимальной рев
            tmp_rev.append(int(rev_num[0][rev]))
        #Определяем PARENT
        tmp_max_rev = max(tmp_rev)
        #Перебираем все ревизии по объекту
        for child_rev in tmp_rev:
            #Берем все, младше PARENT
            if child_rev < tmp_max_rev:
                #Заполняем список младших ревизий
                rev_for_upd.append(child_rev)
        #Идем по списку младших ревизий (которые нужно обновить)
        for upd in rev_for_upd:
            #Времянка для фиксации номера строки, которую сейчас нужно обновить
            tmp_line = 0
            # Заходим в значение ключа по имени объекта, еще раз, теперь, чтобы достать номер строки
            for rev_num2 in dict_name_rev[names]:
                #Условие для поиска нужной строки, по известной ревизии
                if str(upd) in (rev_num2[0][rev]):
                    tmp_line = (int(rev_num2[1][num_line]))
                    #Для того,чтобы запись не дублировалась при перезапуске
                    if 'PARENT' and str(tmp_max_rev) not in old_data_lines[tmp_line]:
                        #Добавляем в нужную строку PARENT ревизию
                        old_data_lines[tmp_line] = old_data_lines[tmp_line].replace(f'{upd};', f'{upd};'
                                                                                           f'PARENT_Rev:{tmp_max_rev}')
    #Переводим список строк в текст
    for line2 in old_data_lines:
        result += line2

#Переписываем исходный файл add_base_name.sql
with open(f'{path_to_folder_build}', 'w') as new_file_build:
    new_file_build.write(result)
"""
    return text


def generate_text_pars_bat():
    text = """echo PARSING LOGS - %2
    
    python parsing_logs.py %1 %2
    
    exit"""
    return text


def generate_text_parsing_logs_py():
    text = r"""#Script for find errors in logs
# -*- coding: cp1251 -*-
import re
import sys
import os
import datetime

name_log = str(sys.argv[2]) 
path_to_folder_logs = str(sys.argv[1]) 

reg_exp_error = r'pls-|ORA-|WARRING|SP2-|Предупреждение|Ошибки|must be declared|compilation errors.$|с ошибками компиляции.$'
reg_exp_dublicate_error = r'^Errors for .{1,70}:$|^Ошибки для .{1,70}$'
start_issue = r'===== ЗАДАЧА  NA-(.*)'
end_issue = r'End: [dD]:\\'
name_script = r'Start: [dD]:\\'
time_start = r'^Time start '
time_end = r'^Time end '
    



# Переменные для фиксации номеров строк: Начала, ошибки, конца, времени выполнения
num_start_issue = 0
num_line_comp_er = 0
num_end_issue = 0
num_line_dubl_er = 0
num_name_script_line = 0
num_time_start = 0
num_time_end = 0

with open(f'{path_to_folder_logs}/{name_log}', 'r') as file_log:
    #Счетчик текущего номера строки
    num_lines = 0
    #Результат - уникальные ошибки
    result = ''
    #Сюда пишутся скрипты выполняемые более 5 минут
    long_run_time = ''
    #Чтение лога построчно
    lines = file_log.readlines()
    for line in lines:
        num_lines += 1
        #Поиск и факсация  номера строки начала.
        #Учитываем, что может быть ошибка ДО старта прогона по задачам
        #Учитываем, что строка End, может отсутствовать
        if re.findall(start_issue, line):
            if num_line_comp_er != 0 and num_start_issue == 0:
                result += '\n==========================================================\n' \
                          'ERROR! Ошибки ДО старта прогона задач\n' \
                          'Возможно при настройке триггера  DDL и DisableSpravSync\n' \
                          f'Проверьте основной лог - {name_log}\n' \
                          '==========================================================\n'
                num_line_comp_er = 0
            if num_line_comp_er != 0 and num_start_issue != 0:
                result += '\n==========================================================\n' \
                          'ERROR! Отсутствует строка "End:" в логе задачи:\n' \
                          f'{lines[num_start_issue]}' \
                          f'Не хватает "/" в конце скрипта ИЛИ прервана связь с ORACLE:\n' \
                          f'Уточните информацию об ошибке в основном логе {name_log}\n' \
                          f'{lines[num_name_script_line].partition("Start: ")[2]}' \
                          '==========================================================\n'
                num_line_comp_er = 0
            num_start_issue = num_lines - 1
        # Поиск и факсация времени начала скрипта
        if re.findall(time_start, line):
            num_time_start = num_lines - 1
        # Поиск и факсация имени скрипта
        if re.findall(name_script, line):
            num_name_script_line = num_lines - 1
        # Поиск и факсация  номера строки с ошибкой, которая возможно дублируется
        if re.findall(reg_exp_dublicate_error, line):
            num_line_dubl_er = num_lines - 1
        #Поиск и факсация  номера строки с ошибкой
        if re.findall(reg_exp_error, line):
            num_line_comp_er = num_lines - 1
        #Поиск и факсация  номера строки конца
        if re.findall(end_issue, line):
            num_end_issue = num_lines - 1
        # Поиск и факсация времени конца скрипта, запись все скриптов дольше 5 минут в long_run_time
        if re.findall(time_end, line) and num_end_issue !=0: #КОСТЫЛЬ!!!
            num_time_end = num_lines - 1
            if num_time_start and num_time_end != 0:
                time_start_issue = datetime.datetime.strptime(lines[num_time_start].lstrip('Time start '),
                                                              '%d/%m/%Y %H:%M:%S ') 
                time_end_issue = datetime.datetime.strptime(lines[num_time_end].lstrip('Time end '),
                                                            '%d/%m/%Y %H:%M:%S ') 
                delta_run = time_end_issue - time_start_issue
                if delta_run > datetime.timedelta(minutes=5):
                    long_run_time += f'\nЗадача: https://jira.psbnk.msk.ru/browse/' \
                                     f'{re.search(r"NA-[0-9]{4,8}", lines[num_start_issue]).group(0)}' \
                                     f'\nДата: {datetime.datetime.now().date()} '  \
                                     f'БД:{lines[num_start_issue].partition("база")[2]}' \
                                     f'Скрипт: {lines[num_name_script_line].partition("Start: ")[2]}' \
                                     f'Выполнялся: ' \
                                     f'{delta_run}\n'
            #Запись в result от начла до конца, только если была ошибка и она не дублируется
            if num_start_issue and num_line_comp_er and num_end_issue and num_line_dubl_er != 0:
                if lines[num_line_dubl_er] not in result:
                    for line_er in range(num_start_issue - 1, num_end_issue + 1):
                        result += lines[line_er]
                #Проверка тела лога на ошибки, если было "ЭХО" num_line_dubl_er != 0
                else:
                    err_bdy = 0
                    for line_er_bdy in range(num_start_issue - 1, num_line_dubl_er):
                        if re.findall(reg_exp_error, lines[line_er_bdy]):
                            err_bdy = 1
                    if err_bdy == 1:
                        # Если была ошибка, добавить тело лога, ДО эхо
                        for line_er_bdy in range(num_start_issue - 1, num_line_dubl_er):
                            result += lines[line_er_bdy]
                        result += lines[num_end_issue]
            # Запись в result от начла до конца, только если была ошибка и она не может дублироваться
            elif num_start_issue and num_line_comp_er and num_end_issue != 0:
                for line_er in range(num_start_issue - 1, num_end_issue + 1):
                    result += lines[line_er]
            # Перевод переменных в 0 после каждой задачи
            num_line_dubl_er = 0
            num_start_issue = 0
            num_line_comp_er = 0
            num_end_issue = 0
            num_name_script_line = 0
            num_time_start = 0
            num_time_end = 0

    #Если был один скрипт ВСЕГО и у него отсутсвует End или ENDA нет в последней задаче
    if num_line_comp_er != 0 and num_start_issue != 0:
        result += '\n==========================================================\n' \
                  'ERROR! Отсутствует строка "End:" в логе задачи:\n' \
                  f'{lines[num_start_issue]}' \
                  f'Не хватает "/" в конце скрипта ИЛИ прервана связь с ORACLE:\n' \
                  f'Уточните информацию об ошибке в основном логе {name_log}\n' \
                  f'{lines[num_name_script_line].partition("Start: ")[2]}' \
                  '==========================================================\n'

#Формирование файла ERROR_*.log, перетирание если такой уже был
if not os.path.isdir(f'{path_to_folder_logs}/ERRORS'):
    os.mkdir(f'{path_to_folder_logs}/ERRORS')
with open(f'{path_to_folder_logs}/ERRORS/ERROR_{name_log}', 'w', encoding='cp1251') as log_error_file:
    if result == '':
        log_error_file.write('\n========================================================================\n'
                             f'====== В тексте лога - {name_log} ОШИБОК НЕ НАЙДЕНО =======\n'
                             '========================================================================\n')
    else:
        log_error_file.write(result)
    log_error_file.write(f'\n=========== Скрипты выполняющиеся более 5 минут ====================\n'
                         f'\n')
    if long_run_time == '':
        log_error_file.write(f'\nВ логе {name_log} длительных скриптов НЕ ОБНАРУЖЕНО\n'
                             f'\n')
    else:
        log_error_file.write(long_run_time)

#Дозапись информации о длительных скриптах в основной лог
with open(f'{path_to_folder_logs}/{name_log}', 'a', encoding='cp1251') as add_long:
    add_long.write(f'\n=========== Скрипты выполняющиеся более 5 минут ====================\n'
                         f'\n')
    if long_run_time == '':
        add_long.write(f'\nВ логе {name_log} длительных скриптов НЕ ОБНАРУЖЕНО\n'
                             f'\n')
    else:
        add_long.write(long_run_time)"""
    return text


def generate_text_base_inv_sql(patch_log_dir, patch_number, bd):
    text = fr"""spool {patch_log_dir}\{patch_number}\{patch_number}_{bd}.log append
set serveroutput on size unlim
set verify off
set pagesize 0
set feedback off
set define on
set sqlblanklines on

prompt;
prompt ====INVALID OBJECTS {bd}==== First 50 names;
prompt;
select sch.OWNER, NVL(a.cnt,0) cnt
from ( select  OWNER, object_name AS CNT
from all_objects where
status = 'INVALID' AND
OWNER IN ('BBR','FACT','NAQ','OD','AFW$','DHW$','IMP$')) a,
( select 'BBR' as OWNER from dual
union  select 'FACT' as OWNER from dual
union  select 'DHW$' as OWNER from dual
union  select 'IMP$' as OWNER from dual
union  select 'NAQ' as OWNER from dual
union  select 'AFW$' as OWNER from dual
union  select 'OD' as OWNER from dual) sch
where A.OWNER (+) = sch.owner
and rownum <= 50
/

prompt
select 'DATE COMPILATION: ', SYSTIMESTAMP
from dual;

spool off
exit;"""
    return text


def generate_text_base_bat(bd, patch_log_dir, patch_number):
    header = fr"""echo off
chcp 1251
title {bd} - %0
mkdir {patch_log_dir}\{patch_number}\
echo ВНИМАНИЕ, будет произведена установка на {bd}!
echo           _____
echo          /    /\
echo         /    /  \
echo        /    /    \
echo       /    /  /\  \
echo      /    /  /  \  \
echo     /    /  /\   \  \
echo    /    /  /  \   \  \
echo   /    /__/____\   \  \
echo  /              \   \  \
echo /________________\   \  \
echo \_____________________\ /
echo !!! {bd} !!! {bd} !!!
pause"""

    body = fr"""
if exist {bd}_BBR.bat call {bd}_BBR.bat
start check_rev.bat d:\svn\ABS\tags\{patch_number}\add_{bd}.sql add_inaf02.sql 
sqlplus OD/od456@{bd}  @d:\svn\ABS\tags\{patch_number}\run\add_{bd}.sql
start pars.bat D:/SVN/_log_/{patch_number} {patch_number}_{bd}.log
sqlplus OD/od456@{bd}  @d:\svn\ABS\tags\{patch_number}\run\recompile.sql
sqlplus OD/od456@{bd}  @d:\svn\ABS\tags\{patch_number}\run\{bd}_inv
start s.bat {patch_log_dir}\{patch_number}\{patch_number}_{bd}.log od {bd}


if exist {bd}_BBR.bat (
  call {bd}_BBR.bat
  sqlplus OD/od456@{bd}  @d:\svn\ABS\tags\{patch_number}\run\recompile.sql
)"""
    return header + body


def generate_text_send_logs():
    text = """dummy"""
    return text
