#/bin/bash
#Do a gnuplot of the Nb values generated in the sim
#via the sim's restrictedGenerator and its calling
#calcNb.  

#input table file should have cols generation<tab>Nb value
#input tsv file from NeEstimator should have generation (1-based)
#in col 2 and Nb estimation in col 11

#naive gnuplot usage, copying mostly
#from http://psy.swansea.ac.uk/staff/carter/gnuplot/gnuplot_histograms.htm"
#Note: if your gnuplot installation doesn't have "term" type "qt", then on linux
#try "x11", or on windows, maybe "wxt" (?).


#requires gnuplot program.

numrequiredargs="7"
numwithopt="8"

mys=$( basename $0 )

if [ "$#" -ne "$numrequiredargs" ] && [ "$#" -ne "$numwithopt" ]
then
	echo "usage: $mys "
	echo "args: "
	echo "       <file with nb values table> "
	echo "       <file, *.tsv,  with NeEstimator or LDNe2 Nb values> "
	echo "       <int, number of generations> "
	echo "       <int, min value for Nb axis (y-axis)"
	echo "       <int, max value for Nb axis (y-axis)"
	echo "       <int, target Nb>"
	echo "       <title> (use \"newline\" to break the title into multiple lines)"
	echo "       optional, <term name> (default is \"qt\", but try \"wxt\" or \"x11 (linux)\" if no qt)"

	exit 0
fi


mytable="$1"
mytsv="$2"
total_gens="$3"
minyval="$4"
maxyval="$5"
target_nb="$6"
mytitle="$7"

if [ "$#" -eq "${numwithopt}" ]
then
	const_term="$8"
else
	const_term="qt"
fi

const_pad_right=0
const_term="qt"
const_width=$( echo "${total_gens}" | awk '{ print $0 * 22 }' )
const_height="600"
const_size="size ${const_width}, ${const_height}"
const_tsv_gen_col="2"
const_tsv_nb_col="11"

#global replacement of newline with 
#literal newline (i.e. 2-line substitution
#breaks title into multi lines:
mynewtitle=${mytitle//newline/
}

gnuplot_statements="set term ${const_term} ${const_size}; \
			set xlabel 'reproductive cycle'; \
			set ylabel 'Nb'; \
			set title '${mynewtitle}'; \
			set yrange [ ${minyval} : ${maxyval} ]; \
			set xrange [ 0 : ${total_gens} + ${const_pad_right} ]; \
			set arrow 1 from 0,${target_nb} to ${total_gens},${target_nb} nohead; \
			set label 'expected' at 0,${target_nb} offset 0.5,1; \
			plot '${mytable}' using 1:2 with linespoints lw 3 t 'sim' , \
						'${mytsv}' using (\$${const_tsv_gen_col}-1):${const_tsv_nb_col} \
								t 'ldne' lw 3 with linespoints ;"

gnuplot -p -e "${gnuplot_statements}"

