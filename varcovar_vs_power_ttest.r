# this code read regression coefficients of variations in var/cov against variations in cardiac and respiratory power pre- and post- RETROICOR and plots them (in terms of box plots) and performs t-tests on them. Regression coefficients (csv file) are generated using connectivity_vs_physspectra.m

csvfile <- '/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/varcovar_vs_power.csv'

data <- read.csv(csvfile)

b <- data$var_b_card
b <- b[ b > (quantile(b,0.25)-1.5*IQR(b)) & b < (quantile(b,0.75)+1.5*IQR(b)) ]
var_b_card <- b
print(t.test(var_b_card))

b <- data$var_b_resp
b <- b[ b > (quantile(b,0.25)-1.5*IQR(b)) & b < (quantile(b,0.75)+1.5*IQR(b)) ]
var_b_resp <- b
print(t.test(var_b_resp))

b <- data$cov_b_card
b <- b[ b > (quantile(b,0.25)-1.5*IQR(b)) & b < (quantile(b,0.75)+1.5*IQR(b)) ]
cov_b_card <- b
print(t.test(cov_b_card))

b <- data$cov_b_resp
b <- b[ b > (quantile(b,0.25)-1.5*IQR(b)) & b < (quantile(b,0.75)+1.5*IQR(b)) ]
cov_b_resp <- b
print(t.test(cov_b_resp))



# plot power spectra over the network
library (ggplot2)

RegCoef <- c(rep('varb_card',length(data$var_b_card)),rep('varb_resp',length(data$var_b_card)),rep('covb_card',length(data$var_b_card)),rep('covb_resp',length(data$var_b_card)))
value <- c(data$var_b_card,data$var_b_resp,data$cov_b_card,data$cov_b_resp)

#Graph
Subject <- c('1','2','3','4','5','6','7','8','9','10','11')
Subject <- c(rep(Subject,4))

#clr <- c(1:length(data$NetcardRelativePowerPost),1:length(data$NetcardRelativePowerPost))
p <- ggplot() +
geom_boxplot(mapping=aes(x=RegCoef, y=value), color=c('red','blue','green','black'))+
geom_point(mapping=aes(x=RegCoef, y=value), size=9, shape=21)+
geom_text(mapping=aes(x=RegCoef, y=value, label=Subject))+
ylab('Regression Coefficients')

print(p)

png(filename='/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/varcovar_vs_power.png')
print(p)
dev.off()

### plot individually

# plot var_b_card

Subject <- c('1','2','3','4','5','6','7','8','9','10','11')

RegCoef1 <- c(rep('',length(data$var_b_card)))
value1 <- data$var_b_card

p1 <- ggplot() +
geom_boxplot(mapping=aes(x=RegCoef1, y=value1), colour='red')+
geom_point(mapping=aes(x=RegCoef1, y=value1), size=9, shape=21)+
geom_text(mapping=aes(x=RegCoef1, y=value1, label=Subject))+
ylab('Regression Coefficients')+
xlab('b_var,card')

# plot var_b_resp
RegCoef2 <- c(rep('',length(data$var_b_resp)))
value2 <- data$var_b_resp
p2 <- ggplot() +
geom_boxplot(mapping=aes(x=RegCoef2, y=value2), colour='blue')+
geom_point(mapping=aes(x=RegCoef2, y=value2), size=9, shape=21)+
geom_text(mapping=aes(x=RegCoef2, y=value2, label=Subject))+
ylab('Regression Coefficients')+
xlab('b_var,resp')

# plot cov_b_card
RegCoef3 <- c(rep('',length(data$cov_b_card)))
Subject <- c('1','2','3','4','5','6','7','8','9','10','11')
value3 <- data$cov_b_card
p3 <- ggplot() +
geom_boxplot(mapping=aes(x=RegCoef3, y=value3), colour='green')+
geom_point(mapping=aes(x=RegCoef3, y=value3), size=9, shape=21)+
geom_text(mapping=aes(x=RegCoef3, y=value3, label=Subject))+
ylab('Regression Coefficients')+
xlab('b_cov,card')

# plot cov_b_resp
RegCoef4 <- c(rep('',length(data$cov_b_resp)))
Subject <- c('1','2','3','4','5','6','7','8','9','10','11')
value4 <- data$cov_b_resp
p4 <- ggplot() +
geom_boxplot(mapping=aes(x=RegCoef4, y=value4), colour='black')+
geom_point(mapping=aes(x=RegCoef4, y=value4), size=9, shape=21)+
geom_text(mapping=aes(x=RegCoef4, y=value4, label=Subject))+
ylab('Regression Coefficients')+
xlab('b_cov,resp')

require(gridExtra)

grid.arrange(p1,p2,p3,p4,ncol=4)


png(filename='/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/varcovar_vs_power_all.png')
grid.arrange(p1,p2,p3,p4,ncol=4)
dev.off()





