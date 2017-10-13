csvfile <- '/home/mkayvanrad/data/healthyvolunteer/respPowerSpectra.csv'

data <- read.csv(csvfile)

print(t.test(data$NetrespRelativePowerPre,data$NetrespRelativePowerPost,paired=TRUE))

print(t.test(data$GMrespRelativePowerPre,data$GMrespRelativePowerPost,paired=TRUE))

print(t.test(data$WMrespRelativePowerPre,data$WMrespRelativePowerPost,paired=TRUE))

# t.test(data$CSFrespRelativePowerPre,data$CSFrespRelativePowerPost,paired=TRUE)

# plot power spectra over the network
library (ggplot2)

RETROICOR <- c(rep('Pre',length(data$NetrespRelativePowerPre)),rep('Post',length(data$NetrespRelativePowerPost)))
value <- c(data$NetrespRelativePowerPre,data$NetrespRelativePowerPost)

#Graph
Subject <- c('1','2','3','4','5','6','7','8','9','10','11','1','2','3','4','5','6','7','8','9','10','11')



#clr <- c(1:length(data$NetrespRelativePowerPost),1:length(data$NetrespRelativePowerPost))
p <- ggplot() +
geom_boxplot(mapping=aes(x=RETROICOR, y=value), color=c('red','blue'))+
geom_point(mapping=aes(x=RETROICOR, y=value), size=9, shape=21)+
geom_text(mapping=aes(x=RETROICOR, y=value, label=Subject))+
ylab('Relative Power')

print(data$NetrespRelativePowerPost-data$NetrespRelativePowerPre)

png(filename='/home/mkayvanrad/data/healthyvolunteer/respPowerSpectra.png')
print(p)
dev.off()

print(p)





