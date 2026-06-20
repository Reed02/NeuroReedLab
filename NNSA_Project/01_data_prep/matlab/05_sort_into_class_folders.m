% Original EEG segments folder
mainFolder = '/Users/cooperledoux/Desktop/EEG_Segments';

% Master output folder where classification folders will be created
masterOutputFolder = fullfile('/Users/cooperledoux/Desktop', 'EEG_Classification');

% Create master output folder if it doesn't exist
if ~exist(masterOutputFolder, 'dir')
    mkdir(masterOutputFolder);
end

cd(mainFolder)

items = dir(mainFolder);
isSubFolder = [items.isdir] & ~ismember({items.name}, {'.','..'});
subFolders = items(isSubFolder);
subFolders = subFolders(startsWith({subFolders.name}, 'Segment of S'));

% Define categories (same as before)
categories = { ...
    'Rest', ...
    'Task1_Real_Left_Fist', ...
    'Task1_Real_Right_Fist', ...
    'Task2_Imag_Left_Fist', ...
    'Task2_Imag_Right_Fist', ...
    'Task3_Real_Both_Fists', ...
    'Task3_Real_Both_Feet', ...
    'Task4_Imag_Both_Fists', ...
    'Task4_Imag_Both_Feet'};

% Create classification folders inside masterOutputFolder
for c = 1:numel(categories)
    categoryFolder = fullfile(masterOutputFolder, categories{c});
    if ~exist(categoryFolder, 'dir')
        mkdir(categoryFolder);
    end
end

% Initialize output struct to store paths (optional)
Files = struct();
for c = 1:numel(categories)
    Files.(categories{c}) = {};
end

% Mapping run number to task as before
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
            
            % Determine destination category folder and copy file
            
            if contains(fname, 'T0')
                destCategory = 'Rest';
            else
                if ~task_map.isKey(runNum)
                    warning('Run %d not mapped to a task', runNum);
                    continue
                end
                task = task_map(runNum);
                
                switch task
                    case 'Task1_Real'
                        if contains(fname, 'T1')
                            destCategory = 'Task1_Real_Left_Fist';
                        elseif contains(fname, 'T2')
                            destCategory = 'Task1_Real_Right_Fist';
                        else
                            continue
                        end
                    case 'Task2_Imag'
                        if contains(fname, 'T1')
                            destCategory = 'Task2_Imag_Left_Fist';
                        elseif contains(fname, 'T2')
                            destCategory = 'Task2_Imag_Right_Fist';
                        else
                            continue
                        end
                    case 'Task3_Real'
                        if contains(fname, 'T1')
                            destCategory = 'Task3_Real_Both_Fists';
                        elseif contains(fname, 'T2')
                            destCategory = 'Task3_Real_Both_Feet';
                        else
                            continue
                        end
                    case 'Task4_Imag'
                        if contains(fname, 'T1')
                            destCategory = 'Task4_Imag_Both_Fists';
                        elseif contains(fname, 'T2')
                            destCategory = 'Task4_Imag_Both_Feet';
                        else
                            continue
                        end
                end
            end
            
            % Copy file to category folder
            destFolder = fullfile(masterOutputFolder, destCategory);
            
            % Use copyfile to copy, overwrite if exists
            try
                copyfile(fullpath, destFolder);
                Files.(destCategory){end+1} = fullfile(destFolder, fname);
            catch ME
                warning('Failed to copy %s to %s\n%s', fullpath, destFolder, ME.message);
            end
        end
        
    catch ME
        warning('Could not access folder: %s\n%s', subPath, ME.message);
    end
    
    cd(mainFolder);
end

fprintf('\nFiles copied and organized under %s\n', masterOutputFolder);

% Optional: display counts
fprintf('\n=== File Count by Category ===\n');
disp(structfun(@numel, Files, 'UniformOutput', false));
