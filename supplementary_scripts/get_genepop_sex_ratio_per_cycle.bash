#!/bin/bash
#Input is a genepop file generated by the negui simulation interface, 
#with age and sex field in each indiv id inside the pops
#sections.  For each pop section, (numbered consecutively) output gives the
#number of females and males, for individuals within the given age range min-max, as 
# popnum\tfemales\tmales\tratio,proportion_females\tproportion_males


numargs="3"

mys=$( basename $0 )

if [ "$#" -ne "$numargs" ]
then
	echo "usage: $mys <genepop file from simulation> <min age> <max age>"
	exit 11
fi

const_delimit_entry=","
const_delimit_idfields=";"
const_idx_idfields="1"
const_idx_sex="2"
const_idx_age="5"

const_male="1"
const_female="2"

gpfile="$1"
minage="$2"
maxage="$3"

popnumber="0"
totfemales="0"
totmales="0"
 
while read myline
do
	lowerline=$( echo "$myline" | awk '{ print tolower( $0 ) }' )

	if [ "$lowerline" == "pop" ]
	then
		if [ "$popnumber" -gt "0" ]
		then
			totindiv="$( expr $totfemales + $totmales )" 
			percmale=$( echo $totmales | awk -v mytot="$totindiv" '{ if( mytot != 0 ){ print $0/mytot} else { print 0 }}' )
			percfemale=$( echo $totfemales | awk -v mytot="$totindiv"  '{ if( mytot !=0 ){ print $0/mytot}else{print 0}}' )
			echo -e "${popnumber}\t${totfemales}\t${totmales}\t${percfemale}\t${percmale}"
		fi

		popnumber=$( expr $popnumber + 1 )
		totfemales="0"
		totmales="0"
	else
		if [ "$popnumber" -gt "0" ]
		then
			idfields=$( echo "$myline" | cut -d ${const_delimit_entry} -f ${const_idx_idfields} )
			thissex=$( echo "$idfields" | cut -d ${const_delimit_idfields} -f ${const_idx_sex} )
			thisage=$( echo "$idfields" | cut -d ${const_delimit_idfields} -f ${const_idx_age} )

			age_is_in_range=$( echo "$thisage" | awk -v nage="$minage" -v xage="$maxage" \
								'{ print (  $0 >= nage && $0 <= xage ) }' )

			if [ "$age_is_in_range" == 1 ]
			then
				if [ "$thissex" == "$const_female" ]
				then
					totfemales=$( expr $totfemales + 1 )
				else
					totmales=$( expr $totmales + 1 )
				fi #if female else male
			fi #if age in range
		fi #end if pop number gt zero
	fi #if pop line else not

done <"$gpfile"

#last pop will not have been reported inside the loop:
totindiv=$( expr $totfemales + $totmales )
percmale=$( echo $totmales | awk -v mytot="$totindiv" '{ if( mytot != 0 ){ print $0/mytot}else{ print 0 }}' )
percfemale=$( echo $totfemales | awk -v mytot="$totindiv" '{ if ( mytot != 0 ){print $0/mytot}else{ print 0}}' )
echo -e "${popnumber}\t${totfemales}\t${totmales}\t${percfemale}\t${percmale}"

exit 0

