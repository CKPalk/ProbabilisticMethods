for f in t1.uai t2.uai t3.uai alarm.uai tree.uai; do
	echo "Running $f";
	python3 hw5.py < $f;
	echo "";
done
