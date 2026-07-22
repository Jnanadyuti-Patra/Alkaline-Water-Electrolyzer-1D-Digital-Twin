function setup_awe_build()
%SETUP_AWE_BUILD Configure short build paths and open the AWE model.
%
% Recommended Windows location:
%   C:\AWE\alkaline-water-electrolyzer-digital-twin
%
% From the repository root, run:
%   addpath('matlab')
%   setup_awe_build

scriptDir = fileparts(mfilename('fullpath'));
projectDir = fileparts(scriptDir);

cacheDir = fullfile(projectDir, 'build', 'cache');
codegenDir = fullfile(projectDir, 'build', 'codegen');

if ~exist(cacheDir, 'dir')
    mkdir(cacheDir);
end
if ~exist(codegenDir, 'dir')
    mkdir(codegenDir);
end

% Remove stale generated files that may contain long cached paths.
staleDirs = {
    fullfile(projectDir, 'slprj'), ...
    cacheDir, ...
    codegenDir
};

for k = 1:numel(staleDirs)
    d = staleDirs{k};
    if exist(d, 'dir')
        try
            rmdir(d, 's');
        catch
            warning('Could not clear %s. Close open model files and retry.', d);
        end
    end
end

mkdir(cacheDir);
mkdir(codegenDir);

Simulink.fileGenControl('set', ...
    'CacheFolder', cacheDir, ...
    'CodeGenFolder', codegenDir, ...
    'createDir', true);

modelFile = fullfile(projectDir, 'model', 'awe_dt.slx');
if ~isfile(modelFile)
    error('Model not found: %s', modelFile);
end

load_system(modelFile);
open_system('awe_dt');

fprintf('AWE model opened successfully.\n');
fprintf('Cache folder: %s\n', cacheDir);
fprintf('Code-generation folder: %s\n', codegenDir);
fprintf('Press Ctrl+D to update the diagram, then simulate the model.\n');
end
