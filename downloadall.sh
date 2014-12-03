I=`ls -l | awk '{print $9}' | tail -n 1 | cut -c 5,6,7,8`
let I=I+1 
while [ $I -lt 2000 ] ; do
    wget http://www.basket.co.il/misc/Stats-XML/isr-$I.xml? > /dev/null 2>&1
    let I=I+1 
done

grep -lrIZ javascript . | xargs -0 rm -f

