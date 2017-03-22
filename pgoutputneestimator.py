'''
Description
Object manages output from the PGOpNeEstimator object

'''
__filename__ = "pgoutputneestimator.py"
__date__ = "20160502"
__author__ = "Ted Cosart<ted.cosart@umontana.edu>"

from os import path
from genomics.popgen import ne2


'''
A value to use in teh parsed output instead 
of pythons None.
'''
MISSING_DATA_ENTRY="NA"

'''
2017_03_20.  Adding support for LDNe2, using
the already created pgldneoutputparser module.
Note that we also renamve some defs in this class
to better specify their source, for example:
__get_parsed_output_data -> __get_ne_estimator_parsed_output_data
'''
import pgldne2outputparser as pgldne
ESTIMATOR_NEESTIMATOR="Ne2"
ESTIMATOR_LDNE="LDNe2"


class PGOutputNeEstimator( object ):

	'''
	Object manages output from the PGOpNeEstimator object
	'''

	OUTPUT_FIELDS = [ "est_type", "case_number", "est_ne","95ci_low","95ci_high", "overall_rsquared",
					"expected_rsquared","indep_comparisons","harmon_mean_samp_size" ]

	NODAT_FIELDS = [ "Individual", "Locus", "Genotype", "NumberLociMissingData" ]

	OUTPUT_TIAGO_ABBREVS = [ "ne","neci05" , "neci975", "or2", "sr2", "indep", "hmean" ]

	def __init__( self, s_input_file, s_run_output_filename, 
										o_bias_adjustor=None, 
										s_estimator_to_use=ESTIMATOR_NEESTIMATOR ):

		#we use the name of the input file to check for NoDat file
		#because NeEstimator uses it to name the file
		self.__run_input_file=s_input_file
		self.__run_output_file=s_run_output_filename

		#a list of lists, each a row
		#of values as given by the output_fields.
		#It is set after NeEstimator generates 
		#the output file and user calls def parseOutput
		self.__parsed_output=None

		#Ne Estimator will generate a "*NoDat.txt"
		#file if it encounters incomplete, missing,
		#or all-zero loci values.  See def parseNoDat:
		self.__parsed_nodat_output=None

		'''
		2017_03_20.  New attribute for support for LDNe2.
		'''
		self.__estimator=s_estimator_to_use

		self.__validate_filenames()
	#end __init__

	def __validate_filenames( self ):
		ls_existing_files=[]	
		for s_name in [ self.__run_output_file ]:
			if path.exists( s_name ):
				ls_existing_files.append( s_name )
			#end if exists add name
		#end for each filename

		if len( ls_existing_files ) > 0:
			s_msg="In " + type( self ).__name__ \
				+ " object instance, def __validate_filenames, " \
				+ "Can't create NeEstimator output files because " \
				+ "the following files already exist:\n  " \
				+ "\n  ".join( ls_existing_files) + "."
			raise Exception( s_msg )
		return
	#end __validate_filenames

	def __get_ne_estimator_parsed_output_data( self ):

		if not path.exists( self.__run_output_file ):
			raise Exception( "in " + type( self ).__name__ + " instance:" \
					+ "cannot parse output.  File, " \
					+ self.__run_output_file \
					+ ", does not exist." )
		#end if no output file

		o_file=open( self.__run_output_file, 'r' )
		o_record=ne2.parse( o_file )

		ddv_results=self.__ne2_record_object_to_dictionary( o_record )

		return ddv_results
	#end __get_ne_estimator_parsed_output_data

	def __convert_parsed_ldne_output_to_this_class_parsed_output( self , ldv_parsed_ldne_output ):

		llv_converted_output=[]

		'''
		These must be in the correct order, as give in OUTPUT_FIELDS,
		so that this class' attribute __parsed_output will list them
		in the correct order.  Note, however that the first 2 values 
		are prepended below as constants
		'''

		OUTPUTFIELDS_NEEST_TO_LDNE={ "est_ne":"ne_estimate",
										"95ci_low":"ci_jackknife_low",
										"95ci_high":"ci_jackknife_hi", 
										"overall_rsquared":"r_squared",
										"expected_rsquared":"exp_r_squared",
										"indep_comparisons":"indep_alleles",
										"harmon_mean_samp_size":"weighted_h_mean" }
		

		for dv_this_parsed_ldne_result in ldv_parsed_ldne_output:


			'''
			These fields, the first 2 values, "esttype", and "case_number",
			are in the output fields, but not in the LDNE2 output, 
			so we supply values.
			'''
			lv_converted_output_this_result=[ "ld", "0" ]

			for s_this_class_field_name in PGOutputNeEstimator.OUTPUT_FIELDS[ 2 : ]:

				s_ldne_field_name=OUTPUTFIELDS_NEEST_TO_LDNE[ s_this_class_field_name ]

				v_val=dv_this_parsed_ldne_result[ s_ldne_field_name ]

				v_processed_val=v_val if v_val is not None else MISSING_DATA_ENTRY

				lv_converted_output_this_result.append(  v_processed_val  )

			#end for each output field
			llv_converted_output.append( lv_converted_output_this_result )
		#end for each row of ldne results

		return llv_converted_output
	#end __convert_parsed_ldne_output_to_this_class_parsed_output
	
	def __set_parsed_output_attribute_using_ldne_data(self):
		o_parser=pgldne.PGLDNe2OutputParser( self.__run_output_file )
		ldv_temp_parsed_output=o_parser.parsed_output
		llv_converted_output = \
				self.__convert_parsed_ldne_output_to_this_class_parsed_output( \
															ldv_temp_parsed_output )
		'''
		Since the default estimator, NeEstimator, can deliver ldne plus other kinds
		of estimations, the default parsed-data format is a list of lists, so we
		wrap our ldne output in a list:
		'''
		self.__parsed_output=llv_converted_output
		return
	#end def __set_parsed_output_attribute_using_ldne_data


	def __set_parsed_output_attribute_using_ne_estimator_data(self):

		INFINITE_VALUE="Inf"

		ddv_results=self.__get_ne_estimator_parsed_output_data()

		self.__parsed_output=[]

		for s_estimation_type in ddv_results:
			i_estimate_count=0
			for fcases in ddv_results[ s_estimation_type ]:
				esttype=s_estimation_type
				estnum=str( i_estimate_count )
				case = fcases[0] 
				ne = case['EstNe']  if case[ 'EstNe' ] is not None else INFINITE_VALUE
				or2 = case['OvRSquare'] 
				sr2 = case['ExpRSquareSample'] 
				indep = case['IndepComp'] 
				hmean = case['HMean'] 
				ne05, ne975 = tuple(case['ParaNe']) 
				#check the indivicual values of the CI's:
				ne05=ne05 if ne05 is not None else INFINITE_VALUE 
				ne975=ne975 if ne975 is not None else INFINITE_VALUE

				lv_rawvals=[ esttype, estnum, ne, ne05, ne975, or2, sr2, indep, hmean  ] 
				lv_vals=[ v_val if v_val is not None else MISSING_DATA_ENTRY for v_val in lv_rawvals ]
				self.__parsed_output.append(  lv_vals  )

				i_estimate_count+=1
			#end for each case
		#end for each estimation type
	#end def __set_parsed_output_attribute_using_ne_estimator_data

	def parseOutput( self ):
		'''
		Fri Jul 22 18:07:53 MDT 2016 -- See 
		def __ne2_record_object_to_dictionary for details on the
		ddv_results fetched below to unwrap the parsed results,
		and the current limitation to estimation type LD

		We assume that for the estimated ne value,
		and its associated CI values, that a value of None in
		the dict returned by ne2.parse def (see above 
		__get_parsed_output_data, reflects
		an "Infinite" value in the origina Ne estimator output
		and so convert it to "Inf,"  convenient for use in R,
		for example, as R uses Inf for Infinity
		
		2017_03_20.  We revise this def to allow getting parsed 
		data from an LDNe2 run, rather than an NeEstimator run. We 
		move the original code that is processing the ne estimator
		data as retrived using pygenomics.genomics.popgen.ne code,
		to a new def specified for the ne-estimator, 
		__set_parsed_output_using_ne_estimator_data.
		This also involves renaming some existing defs, for example:
			__get_parsed_output_data -> __get_ne_estimator_parsed_output_data
		'''
		if self.__estimator==ESTIMATOR_NEESTIMATOR:
			self.__set_parsed_output_attribute_using_ne_estimator_data()
		elif self.__estimator==ESTIMATOR_LDNE:
			self.__set_parsed_output_attribute_using_ldne_data()
		else:
			s_msg="In PGOutputNeEstimator instance, def parseOutput, " \
							+ "The estimator program name is unknown: " \
							+ self.__estimator
			raise Exception( s_msg )
		#end if neestimator, else ldne
		return
	#end parseOutput

	def __ne2_record_object_to_dictionary( self, o_record_obj ):
		'''
		Want to isolate the particulars of the Record objects
		whose attribures each collect for one estimation type, 
		
		We make an iterable out of it so that writing a table 
		of parsed results does not preknowledge of field names 
		for each type.  Hopefully this def can be the sole 
		target of change if the pygenomics, genomics.popgen.ne2 
		parsing code get revised
		'''

		#as of Fri Jul 22 17:50:22 MDT 2016 -- these are the attributes that
		#store NeEstimator output via the pygenomics modules (c.f. __init__.py)
		#genomics.popgen.ne2.  So far we only accept results of type "ld" (because
		#each estimation type has its unique fields, and as such need to be
		#known to be selected for inclusion in this objects output tabular strings.)
		#Here are the Record object attributes used to store NeEstimator output data, 
		#from __init__.py: #	self.freqs_used = []
		#   self.ld = []
		#   self.het = []
		#   self.coanc = []
		#   self.temporal = []
		#note that for now we require "freqs.used" attribute have a single value, 
		#as this is currently the use case for LD NeEstimation, that we parse only for one
		#Ne estimate per population, corresponding to a single minimum allele frequency.

		MAX_ALLOWABLE_NUMBER_FREQS_USED=1
		PARSABLE_ESTIMATION_TYPES=[ "ld" ]
		ds_record_attribute_names=[ "ld", "het", "coanc", "temporal" ]

		#self.freqs_used is in the Record object as a list of floats,
		#and not, as for the other attribures, a list of interables 
		#i.e. in this case would be sensibly a  list of lists of floats,
		#but I think Tiago must be inferring that number of freqs is always
		#constant across all estimates for a given NeEstimator run, hence:
		i_total_number_of_allele_freq_vals_used=len( o_record_obj.freqs_used )

		if i_total_number_of_allele_freq_vals_used > MAX_ALLOWABLE_NUMBER_FREQS_USED:
			s_msg="In PGOutputNeEstimator instance, found estimation results of type, " \
						+ s_record_attribute_name \
						+ ".  Current output parsing limits Estimation to using at most " \
						+ str( MAX_ALLOWABLE_NUMBER_FREQS_USED ) \
						+ ", but  ne2 Record object shows that " \
						+ str( i_total_number_of_allele_freq_vals_used ) \
						+ " were used."
			raise Exception ( s_msg )
		#end if non-single number of (minimum) allele 
		#frequencies were used in the run

		ddv_results={}
		for	s_record_attribute_name in ds_record_attribute_names:
			lv_results=getattr( o_record_obj, s_record_attribute_name )
			i_num_results=len( lv_results )
			if i_num_results > 0 and s_record_attribute_name not in PARSABLE_ESTIMATION_TYPES:
				s_msg = "In PGOutputNeEstimator instance, found estimation results of type, " \
						+ s_record_attribute_name \
						+ ".  Currently the following are the only estimate types " \
						+ "that this object can parse: " + str( PARSABLE_ESTIMATION_TYPES ) \
						+ "."
				raise Exception( s_msg )
			#end if non-parsable  estimation type
			ddv_results[ s_record_attribute_name ] = lv_results
		#end for each record attribute giving an estimation type

		return ddv_results
	#end def __ne2_record_object_to_dictionary

	def __get_name_nodat_file( self ):
		'''
		we  use the input file name (supplied in __init__
		to check for the nodat file:
		'''

		NODAT_TAG="NoDat.txt"
		s_nodatfile=self.__run_input_file + NODAT_TAG

		if path.exists( s_nodatfile ):
			return s_nodatfile
		else:
			return None
		#end if nodat file exists, else not

		return None

	#end __get_name_nodat_file

	def getNoDatFileName( self ):
		return self.__get_name_nodat_file()
	#end getNoDatFileName

	def parseNoDatFile( self ):
		'''
		This def is provisional, since I have only seen
		a few of the *NoDat.txt files generated by
		NeEstimator (v2). I base the parsing on examples like this:

		Population 1 [OmyLGRA12S_0213]	
		-----------------------------------------------------------
		Individual       Locus         Genotype     Number of Loci
                                          with missing data
		       1            9             0000             4   
		----------------------------------------------------------	
		
	
		
		However thin the ground, this def assumes

		1. multipop results will simply have more table entries
		like the one above.

		2. If a line in the NeEstimator's "*NoDat.txt" file
		starts with the value below in COLHEADSTART, and 
		contains the other column keywords given below
		in COLSINCLUDE, that is must be the header and
		also that the data follows after one mostly line blank
		but for a tag on the last column header

		3. Population name entry for each table is uniqely
		located by the line starting with value below in POPLINESTART
		'''


		POPLINESTART="Population"
		COLHEADSTART="Individual"       
		COLSINCLUDE=[ "Locus", "Genotype", "Number of Loci" ]
		ENDTABLELINESTART="----------------------"	

		s_name=self.__get_name_nodat_file()

		if s_name is None:
			return
		#end return if no nodat file

		self.__parsed_nodat_output=[]

		o_file=open( s_name )

		b_found_header=False
		i_table_lines_count=0
		s_currpop=""
		for s_line in o_file:

			i_num_match=0
			if s_line.startswith( POPLINESTART ):
				#we replace spaces in the pop name:
				s_currpop=s_line.strip().replace( " ", "_" )
			elif s_line.startswith(COLHEADSTART):
				lb_trues=[ s_col in s_line for s_col in COLSINCLUDE ]
				if sum( lb_trues ) == len( COLSINCLUDE ):
					b_found_header=True
					i_table_lines_count=0
				#end if all header names in line
			else:
				#first line after header is more header:
				if b_found_header and i_table_lines_count > 1:
					#if end of table for currpop, 
					#reset flag, line counts
					if s_line.startswith( ENDTABLELINESTART ):
						b_found_header=False
						i_table_lines_count=0
					else:
						i_table_lines_count+=1
						#NoDat.txt files data cols
						#are seperated by multiple space chars,
						#so we use the default split to
						#list only non-space as items:	
						ls_vals=s_line.strip().split() 
						#first col is the pop name
						self.__parsed_nodat_output.append( [ s_currpop ] \
								+ [ s_val for s_val in ls_vals ] )
					#end if end-table line, else data
				#end if header's been found and we're past the non-date line
			#end if pop line else header line, else some other line
		#end for each line in nodat file

		o_file.close()
		return
	#end parseNoDatFile

	def __write_parsed_output_files_tiago_format( self, s_file_ne_vals, s_file_other_vals, b_append=True ):
		'''
		file formats as used by Tiago in his original ne2.py
		one file has just the ne vals and CI's, and another
		has means Rsquareds, etc


		As of Fri Jul 22 18:30:50 MDT 2016, this code is very
		close to a simple copy of code from Tiago's code, and
		is meant to parse and write LD estimation only.  This
		limitaion is also applied to def
		__write_parsed_data_lines_as_string.  See def 
		__ne2_record_object_to_dictionary for deatils
		on the conversion of the ne2.Record object's conversion
		to the ddv_results dictionary, and current limitations
		for parsing NeEstimator output.
		'''
		ddv_results=self.__get_ne_estimator_parsed_output_data()

		mNes = []
		mOr2s = []
		mSmpr2s = []
		mNesPow = []
		mNesCI = []
		mIndep = []
		mHMean = []
		for s_estimation_type in ddv_results:
			for fcases in dv_results.ld:
				case = fcases[0]
				ne = case['EstNe']
				or2 = case['OvRSquare']
				sr2 = case['ExpRSquareSample']
				indep = case['IndepComp']
				hmean = case['HMean']
				ne05, ne975 = tuple(case['ParaNe'])
				mNes.append(ne)
				mOr2s.append(or2)
				mSmpr2s.append(sr2)
				mNesCI.append((ne975, ne05))
				mIndep.append(indep)
				mHMean.append(hmean)
			#end for each item 
		#end for each estimation type

		if b_append==True:
			s_open_flag='a'
		else:
			s_open_flag='w'
		#end if append else overwrite

		o_parsed_output_ne_vals= open( s_file_ne_vals, s_open_flag )
		o_parsed_output_ne_vals.write( str(mNes) + "\n"  )
		o_parsed_output_ne_vals.write( str(mNesCI) + "\n" )
		o_parsed_output_ne_vals.close()

		o_parsed_output_other_vals=open( s_file_other_vals, s_open_flag )
		o_parsed_output_other_vals.write(str(mOr2s) + "\n" )
		o_parsed_output_other_vals.write(str(mSmpr2s) + "\n" )
		o_parsed_output_other_vals.write(str(mIndep) + "\n" )
		o_parsed_output_other_vals.write(str(mHMean) + "\n" )
		o_parsed_output_ne_vals.close()

		return
	#end def __write_parsed_output_files_tiago_format

	def __write_parsed_data_lines_as_string( self, llv_parsed_output, s_delim="\t" ):
		s_parsed_output=""
		for lv_output_line in llv_parsed_output:
			s_parsed_output += \
			s_delim.join( [ str(v_entry) for v_entry in lv_output_line ] )
			s_parsed_output += "\n"
		#end for each line of parsed output

		return s_parsed_output
	#end __write_parsed_data_lines_as_string

	def __saveNoDatInfo( self ):
		return
	#end __saveNoDatInfo

	def getColumnNumberForFieldName( self, s_name ):
		i_column_number=None
		
		try:
			i_column_number=PGOutputNeEstimator.OUTPUT_FIELDS.index( s_name )
		except ValueError as ve:
			s_msg="In PGOutputNeEstimator instance, " \
						+ "def getColumnNumberForFieldName, " \
						+ "no column named " + str( s_name ) \
						+ "."
			raise Exception( s_msg )
			
		#end try, except

		return i_column_number
	#end

	@property
	def parsed_output( self ):
		llv_parsed_output=None

		if self.__parsed_output is not None:
			#remmed out in favor of delivering
			#the original output of def parsedOutput
			#s_parsed_out = self.__write_parsed_data_lines_as_string( \
			#								self.__parsed_output )
			llv_parsed_output=self.__parsed_output	
		#end if no parsed output

		return llv_parsed_output
	#end parsed_output

	@property
	def parsed_nodat_info( self ):

		s_parsed_out=None

		if self.__parsed_nodat_output is not None:
			s_parsed_out = self.__write_parsed_data_lines_as_string( \
					self.__parsed_nodat_output )
		#end if no parsed output

		return s_parsed_out

	#end parsed_nodat_info

	@property
	def run_output_file( self ):
		return self.__run_output_file
	#end run_output_file

	@run_output_file.setter
	def output_file( self, s_name ):
		self.__run_output_file=s_name
		return
	#end run_output_file

	@property
	def run_input_file( self ):
		return self.__run_input_file
	#end run_input_file

	@run_input_file.setter
	def run_input_file( self, s_name ):
		self.__run_input_file=s_name
		return
	#end run_input_file
	
	@property 
	def output_fields( self ):
		return PGOutputNeEstimator.OUTPUT_FIELDS
	#end output_fields


#end class PGOutputNeEstimator

