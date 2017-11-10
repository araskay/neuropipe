csvfile <- '/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/lowPowerSpectra.csv'

data <- read.csv(csvfile)

print(t.test(data$NetlowRelativePowerPost,data$NetlowRelativePowerPre,paired=TRUE))

# plot power spectra over the network
library (ggplot2)

RETROICOR <- c(rep('Pre',length(data$NetlowRelativePowerPre)),rep('Post',length(data$NetlowRelativePowerPost)))
value <- c(data$NetlowRelativePowerPre,data$NetlowRelativePowerPost)

#Graph
Subject <- c('1','2','3','4','5','6','7','8','9','10','11','1','2','3','4','5','6','7','8','9','10','11')

p <- ggplot() +
geom_boxplot(mapping=aes(x=RETROICOR, y=value), color=c('red','blue'))+
geom_point(mapping=aes(x=RETROICOR, y=value), size=9, shape=21)+
geom_text(mapping=aes(x=RETROICOR, y=value, label=Subject))+
ylab('Normalized Power')

print(data$NetlowRelativePowerPost-data$NetlowRelativePowerPre)

png(filename='/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/lowPowerSpectra.png')
print(p)
dev.off()

print(p)





