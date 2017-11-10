# This code reads cardiac spectral powers pre- and post- retroicor for different subjects from the csv file and (1) performs a matched pairs t-test under the null hypothesis that there is no difference in cardiac power pre- and post- retroicor, and (2) plots the distribution of powers pre- and post- retroicor for all subjects in boxplots.

csvfile <- '/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/cardPowerSpectra.csv'

data <- read.csv(csvfile)

print(t.test(data$NetcardRelativePowerPost,data$NetcardRelativePowerPre,paired=TRUE))

# print(t.test(data$GMcardRelativePowerPost,data$GMcardRelativePowerPre,paired=TRUE))

# print(t.test(data$WMcardRelativePowerPost,data$WMcardRelativePowerPre,paired=TRUE))

# print(t.test(data$CSFcardRelativePowerPost,data$CSFcardRelativePowerPre,paired=TRUE))

# plot power spectra over the network
library (ggplot2)

RETROICOR <- c(rep('Pre',length(data$NetcardRelativePowerPre)),rep('Post',length(data$NetcardRelativePowerPost)))
value <- c(data$NetcardRelativePowerPre,data$NetcardRelativePowerPost)

#Graph
Subject <- c('1','2','3','4','5','6','7','8','9','10','11','1','2','3','4','5','6','7','8','9','10','11')

p <- ggplot() +
geom_boxplot(mapping=aes(x=RETROICOR, y=value), color=c('red','blue'))+
geom_point(mapping=aes(x=RETROICOR, y=value), size=9, shape=21)+
geom_text(mapping=aes(x=RETROICOR, y=value, label=Subject))+
ylab('Normalized Power')

print(data$NetcardRelativePowerPost-data$NetcardRelativePowerPre)

png(filename='/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/cardPowerSpectra.png')
print(p)
dev.off()

print(p)





