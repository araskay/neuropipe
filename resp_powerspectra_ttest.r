# This code reads respiratory spectral powers pre- and post- retroicor for different subjects from the csv file and (1) performs a matched pairs t-test under the null hypothesis that there is no difference in respiratory power pre- and post- retroicor, and (2) plots the distribution of powers pre- and post- retroicor for all subjects in boxplots.

csvfile <- '/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/respPowerSpectra.csv'

data <- read.csv(csvfile)

print(t.test(data$NetrespRelativePowerPost,data$NetrespRelativePowerPre,paired=TRUE))

# print(t.test(data$GMrespRelativePowerPost,data$GMrespRelativePowerPre,paired=TRUE))

# print(t.test(data$WMrespRelativePowerPost,data$WMrespRelativePowerPre,paired=TRUE))

# print(t.test(data$CSFrespRelativePowerPost,data$CSFrespRelativePowerPre,paired=TRUE))

# plot power spectra over the network
library (ggplot2)

RETROICOR <- c(rep('Pre',length(data$NetrespRelativePowerPre)),rep('Post',length(data$NetrespRelativePowerPost)))
value <- c(data$NetrespRelativePowerPre,data$NetrespRelativePowerPost)

#Graph
Subject <- c('1','2','3','4','5','6','7','8','9','10','11','1','2','3','4','5','6','7','8','9','10','11')

p <- ggplot() +
geom_boxplot(mapping=aes(x=RETROICOR, y=value), color=c('red','blue'))+
geom_point(mapping=aes(x=RETROICOR, y=value), size=9, shape=21)+
geom_text(mapping=aes(x=RETROICOR, y=value, label=Subject))+
ylab('Normalized Power')

print(data$NetrespRelativePowerPost-data$NetrespRelativePowerPre)

png(filename='/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/respPowerSpectra.png')
print(p)
dev.off()

print(p)





