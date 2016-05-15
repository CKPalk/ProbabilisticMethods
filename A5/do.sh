


for f in t1.uai t2.uai t3.uai alarm.uai tree.uai; do
	expected_val=0
	case $f in
		t1.uai) 	expected_val=54 	;;
		t2.uai) 	expected_val=34.059 ;;
		t3.uai) 	expected_val=23.1858;;
		alarm.uai) 	expected_val=41.9525;;
		tree.uai) 	expected_val=18		;;
	esac

	echo "Running $f and expecting $expected_val";
	python3 hw5.py < $f
	echo "";
done
