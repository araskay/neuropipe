csvfile <- '/home/mkayvanrad/data/healthyvolunteer/processed/varcovar_vs_power.csv'

data <- read.csv(csvfile)

print(t.test(data$var_b_card))

print(t.test(data$var_b_resp))

print(t.test(data$cov_b_card))

print(t.test(data$cov_b_resp))



# plot power spectra over the network
library (ggplot2)

RegCoef <- c(rep('varb_card',length(data$var_b_card)),rep('varb_resp',length(data$var_b_card)),rep('covb_card',length(data$var_b_card)),rep('covb_resp',length(data$var_b_card)))
value <- c(data$var_b_card,data$var_b_resp,data$cov_b_card,data$cov_b_resp)

#Graph
Subject <- c('1','2','3','4','5','6','7','8','9','10')
Subject <- c(rep(Subject,4))



#clr <- c(1:length(data$NetcardRelativePowerPost),1:length(data$NetcardRelativePowerPost))
p <- ggplot() +
geom_boxplot(mapping=aes(x=RegCoef, y=value), color=c('red','blue','green','black'))+
geom_point(mapping=aes(x=RegCoef, y=value), size=9, shape=21)+
geom_text(mapping=aes(x=RegCoef, y=value, label=Subject))+
ylab('Regression Coefficients')

print(p)

png(filename='/home/mkayvanrad/data/healthyvolunteer/processed/varcovar_vs_power.png')
print(p)
dev.off()







