mainFolder = '/Users/cooperledoux/Desktop/EEG_Segments';
cd(mainFolder)

items = dir(mainFolder);
isSubFolder = [items.isdir] & ~ismember({items.name}, {'.','..'});
subFolders = items(isSubFolder);
subFolders = subFolders(startsWith({subFolders.name}, 'Segment of S'));

% Initialize output
Files.Rest = {};

Files.Task1_Real_Left_Fist = {};
Files.Task1_Real_Right_Fist = {};
Files.Task2_Imag_Left_Fist = {};
Files.Task2_Imag_Right_Fist = {};

Files.Task3_Real_Both_Fists = {};
Files.Task3_Real_Both_Feet = {};
Files.Task4_Imag_Both_Fists = {};
Files.Task4_Imag_Both_Feet = {};

% Map run number to task and real/imagined
task_map = containers.Map(...
    {3,7,11,4,8,12,5,9,13,6,10,14}, ...
    {'Task1_Real','Task1_Real','Task1_Real', ...
     'Task2_Imag','Task2_Imag','Task2_Imag', ...
     'Task3_Real','Task3_Real','Task3_Real', ...
     'Task4_Imag','Task4_Imag','Task4_Imag'});

for k = 1:numel(subFolders)
    subPath = fullfile(mainFolder, subFolders(k).name);
    try
        cd(subPath);
        subName = subFolders(k).name;
        token = regexp(subName, 'R(\d+)', 'tokens');
        if isempty(token)
            warning('Could not extract run number from %s', subName);
            continue
        end
        runNum = str2double(token{1}{1});
        
        files_set = [dir('*T0.set'); dir('*T1.set'); dir('*T2.set')];
        files_fdt = [dir('*T0.fdt'); dir('*T1.fdt'); dir('*T2.fdt')];
        matches = [files_set; files_fdt];
        
        for f = 1:numel(matches)
            fname = matches(f).name;
            fullpath = fullfile(subPath, fname);
            
            if contains(fname, 'T0')
                Files.Rest{end+1} = fullpath;
                continue
            end
            
            if ~task_map.isKey(runNum)
                warning('Run %d not mapped to a task', runNum);
                continue
            end
            
            task = task_map(runNum);
            
            switch task
                case 'Task1_Real'
                    if contains(fname, 'T1')
                        Files.Task1_Real_Left_Fist{end+1} = fullpath;
                    elseif contains(fname, 'T2')
                        Files.Task1_Real_Right_Fist{end+1} = fullpath;
                    end
                case 'Task2_Imag'
                    if contains(fname, 'T1')
                        Files.Task2_Imag_Left_Fist{end+1} = fullpath;
                    elseif contains(fname, 'T2')
                        Files.Task2_Imag_Right_Fist{end+1} = fullpath;
                    end
                case 'Task3_Real'
                    if contains(fname, 'T1')
                        Files.Task3_Real_Both_Fists{end+1} = fullpath;
                    elseif contains(fname, 'T2')
                        Files.Task3_Real_Both_Feet{end+1} = fullpath;
                    end
                case 'Task4_Imag'
                    if contains(fname, 'T1')
                        Files.Task4_Imag_Both_Fists{end+1} = fullpath;
                    elseif contains(fname, 'T2')
                        Files.Task4_Imag_Both_Feet{end+1} = fullpath;
                    end
            end
        end
    catch ME
        warning('Could not access %s\n%s', subPath, ME.message);
    end
    cd(mainFolder);
end

% Display counts
fprintf('\n=== File counts per category ===\n');
disp(structfun(@numel, Files, 'UniformOutput', false));
