rdom () { local IFS=\> ; read -d \< E C ;}

wget http://www.basket.co.il/misc/leagueXML/games.xml
while rdom; do
    if [[ $E = ExternalID ]]; then
	if [[ $C != 0 ]]; then
	    ISR_GAME="isr-$C.xml"
	    GAME="$C.xml"

	    if [ -e $ISR_GAME ] ; then
		echo h > /dev/null
	    else
		wget http://www.basket.co.il/misc/Stats-XML/$ISR_GAME > /dev/null 2>&1
		echo $ISR_GAME
	    fi

	    if [ -e $GAME ] ; then
		echo h > /dev/null
	    else
		wget http://www.basket.co.il/misc/Stats-XML/$GAME > /dev/null 2>&1
	    fi
	fi
    fi
done < games.xml

grep -lrIZ javascript . | xargs -0 rm -f
rm games.xml*
