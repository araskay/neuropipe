csvfile <- '/home/mkayvanrad/data/healthyvolunteer/cardPowerSpectra.csv'

data <- read.csv(csvfile)

print(t.test(data$NetcardRelativePowerPre,data$NetcardRelativePowerPost,paired=TRUE))

print(t.test(data$GMcardRelativePowerPre,data$GMcardRelativePowerPost,paired=TRUE))

print(t.test(data$WMcardRelativePowerPre,data$WMcardRelativePowerPost,paired=TRUE))

# t.test(data$CSFcardRelativePowerPre,data$CSFcardRelativePowerPost,paired=TRUE)

# plot power spectra over the network
library (ggplot2)

RETROICOR <- c(rep('Pre',length(data$NetcardRelativePowerPre)),rep('Post',length(data$NetcardRelativePowerPost)))
value <- c(data$NetcardRelativePowerPre,data$NetcardRelativePowerPost)

#Graph
Subject <- c('1','2','3','4','5','6','7','8','9','10','11','1','2','3','4','5','6','7','8','9','10','11')



#clr <- c(1:length(data$NetcardRelativePowerPost),1:length(data$NetcardRelativePowerPost))
p <- ggplot() +
geom_boxplot(mapping=aes(x=RETROICOR, y=value), color=c('red','blue'))+
geom_point(mapping=aes(x=RETROICOR, y=value), size=9, shape=21)+
geom_text(mapping=aes(x=RETROICOR, y=value, label=Subject))+
ylab('Relative Power')

print(data$NetcardRelativePowerPost-data$NetcardRelativePowerPre)

png(filename='/home/mkayvanrad/data/healthyvolunteer/cardPowerSpectra.png')
print(p)
dev.off()

print(p)





