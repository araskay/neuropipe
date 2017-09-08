import workflow
subjects=workflow.getsubjects('/home/mkayvanrad/code/pipeline/temp/subjects2.txt')

print('# subjects',len(subjects))
for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            print('Subject:',subj.ID,sess.ID,run.seqname)

workflow.savesubjects('/home/mkayvanrad/code/pipeline/temp/subjects3.txt',subjects)