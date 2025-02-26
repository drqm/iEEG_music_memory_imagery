base_path = 'C:/Users/dariq/Dropbox/projects/iEEG_music_memory_imagery';
%input_dir = [base_path '/stimuli_working_memory/'];
%output_dir = [base_path '/stimuli_working_memory_48k/'];
% input_dir = [base_path '/StimuliBlock1_Recognition/'];
% output_dir = [base_path '/StimuliBlock1_Recognition_48k/'];
input_dir = [base_path '/StimuliBlock1_Encoding/'];
output_dir = [base_path '/StimuliBlock1_Encoding_48k/'];
tones = dir([input_dir '*.wav']);
new_fs = 48000;
for t = 1:length(tones)
    [wav,fs] = audioread([input_dir tones(t).name]);
    wav = mean(wav,2);
    wav = resample(wav,new_fs,fs);
    audiowrite([output_dir,tones(t).name],wav,new_fs);
end

