# This code reads cardiac, respiratory, and low-frequency spectral powers from the corresponding csv files and plots them all together. For matched pairs t-tests and/or individual plots see card_powerspectra_ttest.r, resp_powerspectra_ttest.r, and low_powerspectra_ttest.r.

library (ggplot2)

csvfile_card <- '/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/cardPowerSpectra.csv'
csvfile_resp <- '/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/respPowerSpectra.csv'
csvfile_low <- '/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/lowPowerSpectra.csv'

data_card <- read.csv(csvfile_card)

RETROICOR_card <- c(rep('Pre',length(data_card$NetcardRelativePowerPre)),rep('Post',length(data_card$NetcardRelativePowerPost)))
value_card <- c(data_card$NetcardRelativePowerPre,data_card$NetcardRelativePowerPost)

Subject <- c('1','2','3','4','5','6','7','8','9','10','11','1','2','3','4','5','6','7','8','9','10','11')

p1 <- ggplot() +
geom_boxplot(mapping=aes(x=RETROICOR_card, y=value_card), color=c('red','blue'))+
geom_point(mapping=aes(x=RETROICOR_card, y=value_card), size=9, shape=21)+
geom_text(mapping=aes(x=RETROICOR_card, y=value_card, label=Subject))+
ylab('Normalized Power')+
xlab('Cardiac Power')


data_resp <- read.csv(csvfile_resp)

RETROICOR_resp <- c(rep('Pre',length(data_resp$NetrespRelativePowerPre)),rep('Post',length(data_resp$NetrespRelativePowerPost)))
value_resp <- c(data_resp$NetrespRelativePowerPre,data_resp$NetrespRelativePowerPost)

Subject <- c('1','2','3','4','5','6','7','8','9','10','11','1','2','3','4','5','6','7','8','9','10','11')

p2 <- ggplot() +
geom_boxplot(mapping=aes(x=RETROICOR_resp, y=value_resp), color=c('red','blue'))+
geom_point(mapping=aes(x=RETROICOR_resp, y=value_resp), size=9, shape=21)+
geom_text(mapping=aes(x=RETROICOR_resp, y=value_resp, label=Subject))+
ylab('Normalized Power')+
xlab('Respiratory Power')

data_low <- read.csv(csvfile_low)

RETROICOR_low <- c(rep('Pre',length(data_low$NetlowRelativePowerPre)),rep('Post',length(data_low$NetlowRelativePowerPost)))
value_low <- c(data_low$NetlowRelativePowerPre,data_low$NetlowRelativePowerPost)

Subject <- c('1','2','3','4','5','6','7','8','9','10','11','1','2','3','4','5','6','7','8','9','10','11')

p3 <- ggplot() +
geom_boxplot(mapping=aes(x=RETROICOR_low, y=value_low), color=c('red','blue'))+
geom_point(mapping=aes(x=RETROICOR_low, y=value_low), size=9, shape=21)+
geom_text(mapping=aes(x=RETROICOR_low, y=value_low, label=Subject))+
ylab('Normalized Power')+
xlab('Low-frequency Power')

require(gridExtra)

grid.arrange(p1,p2,p3,ncol=3)


png(filename='/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/allPowerSpectra.png')
grid.arrange(p1,p2,p3,ncol=3)
dev.off()
