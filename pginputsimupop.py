'''
Description

Retrieves and prepares data needed to run simuPop.  See class description.

'''
__filename__ = "pginputsimupop.py"
__date__ = "20160126"
__author__ = "Ted Cosart<ted.cosart@umontana.edu>"

START_LAMBDA_IGNORE=99999
LAMBDA_IGNORE=1.0

import os
from ConfigParser import ConfigParser
from ConfigParser import NoSectionError

class PGInputSimuPop( object ):
	'''
	Object meant to fetch parameter values and prepare them for 
	use in a simuPop simulation.  

	Object to be passed to a PGOpSimuPop object, which is, in turn,
	passed to a PGGuiSimuPop object, so that the widgets can then access
	defs in this input object, in order to, for example, show or allow
	changes in parameter values for users before they run the simulation.
	'''
	def __init__( self, s_config_file = None, o_model_resources = None, o_param_names=None ):
		'''
		param s_config_file, parseable by ConfigParser, params for 
			running simuPop, or references into the resources
			object.  Note that this config file must have a
			section called "model" with a "name" option, which
			should match a name key in the PGModelResources objects
			dictionary.

		param o_model_resources, object of type PGModelResources,
			whose member dictionary has the sub-dictionaries
			that have the param values not given in the config file,
			such as fecundity and reproductive values, and exposed
			via calls to is getValue def.

		param o_param_names, object ot type PGParamSet,
			that gives a shortname (attribute name)
			and a longname (readable text), for each 
			param in the simpupop configuration attribute 
			list
		'''

		self.__config_parser=None
		self.__resources=o_model_resources
		self.__param_names=o_param_names

		#for writing current param values to a new config file,
		#and updated as attributes are created either by reading
		#in the orig config file in def get_config, or by adding the parameter
		#in def addParameter:
		self.__config_file_option_name_by_attribute_name={}		
		self.__config_file_section_name_by_attribute_name={}

		if s_config_file is not None:
			self.__full_config_file_name=s_config_file
			self.config_file=os.path.basename( s_config_file )
			self.__make_config_parser( s_config_file )
		#end if we have a conf file

		return
	#end def __init__
  
	def __find_resources( self, s_model_name, s_config_file_value ):
		'''
		if eval works, then the values are in the original conf file.
		else if eval call raises NameError, then it names a value 
		the conf file gave in form dict[ species ], one of the 
		dictionaries that should be available in the PGModelResources 
		member instance.
		'''
		v_value=None

		try: 

			v_value=eval (s_config_file_value )

		except NameError, ne:

			if self.__resources is not None:
				
				ls_dict_item_split=s_config_file_value.split( "[" )
				s_dict_name=( ls_dict_item_split[ 0 ] ).strip()
				s_gamma_list_key=ls_dict_item_split[ len( ls_dict_item_split ) - 1 ]
				s_gamma_list_key=s_gamma_list_key.replace( "]", "" )

				#resoures configuration file, written using the dictinaries in tiagos
				#myUtils file, has a main section 'resources' for 
				#values that tiago coded dict[ species ]=value, where value is a list
				#or int, but also has dictionary values (gammaAMale has
				#dictionary value), which require the dict name to be a section name
				#so that the key or keys can be used for the key=value portion
				v_value=self.__resources.getLifeTableValue( s_model_name, s_dict_name, s_gamma_list_key )

				if v_value is None:
					v_value=self.__resources.getLifeTableValue( s_model_name, 'resources', s_dict_name )
				#end if we got none returned when we tried to name the section, then  use 'resources'


			else:
				raise Exception ( "input object for PGInputSimuPop has no resources, " \
						"but the value in the configuration file parser , " \
						+ s_config_file_value + " can't be resolved by eval(): " \
						+ str( ne ) )
			#end if we have a resources file to deal
			#with the NameError value, else not
		#end try  to evaluate the string, excpet, go to resources

		return v_value

	#end __find_resources

	def __make_config_parser( self, s_resources_file_name ):
		self.__config_parser = ConfigParser()
		self.__config_parser.read(s_resources_file_name )
	#end __maake_config_parser

	def __update_attribute_config_file_info( self, s_attribute_name, s_section_name, s_option_name ):
		'''
		updates the member dictionaries that tie attribute names to
		config file sections and option names, to facilitate
		writing the current attribute set back to a configuration file
		'''

		self.__config_file_section_name_by_attribute_name[ s_attribute_name ]=s_section_name
		self.__config_file_option_name_by_attribute_name[ s_attribute_name ]=s_option_name
		return
	#end __update_attribute_config_file_info


	def __get_config( self ):

		config=self.__config_parser

		s_model_name=config.get( "model", "name" )


		self.model_name=s_model_name
		
		self.__update_attribute_config_file_info( "model_name", "model", "name" )

		self.N0 = config.getint("pop", "N0")
		self.__update_attribute_config_file_info( "N0", "pop", "N0" )

		self.popSize = config.getint("pop", "popSize")
		self.__update_attribute_config_file_info( "popSize", "pop", "popSize" )

		self.ages = self.__find_resources( s_model_name,  config.get("pop", "ages"))
		self.__update_attribute_config_file_info( "ages", "pop", "ages" )

		if config.has_option("pop", "isMonog"):
			self.isMonog = config.getboolean("pop", "isMonog")
		else:
			self.isMonog = False
		#end if isMonog else not
		self.__update_attribute_config_file_info( "isMonog", "pop", "isMonog" )


		if config.has_option("pop", "forceSkip"):
			self.forceSkip = config.getfloat("pop", "forceSkip") / 100
		else:
			self.forceSkip = 0
		#end if forceSkip, else not
		self.__update_attribute_config_file_info( "forceSkip", "pop", "forceSkip" )

		if config.has_option("pop", "skip"):
			self.skip = self.__find_resources( s_model_name,  config.get("pop", "skip"))
		else:
			self.skip = None
		#end if skip, else not
		self.__update_attribute_config_file_info( "skip", "pop", "skip" )


		if config.has_option("pop", "litter"):
			self.litter = self.__find_resources( s_model_name,  config.get("pop", "litter"))
		else:
			self.litter = None
	    #end if config has litter
		self.__update_attribute_config_file_info( "litter", "pop", "litter" )

		if config.has_option("pop", "male.probability"):
			self.maleProb = config.getfloat("pop", "male.probability")
		else:
			self.maleProb = 0.5
		#end if male.prob, else not
		self.__update_attribute_config_file_info( "maleProb", "pop", "male.probability" )

		if config.has_option("pop", "gamma.b.male"):
			self.doNegBinom = True
			self.gammaAMale = self.__find_resources( s_model_name,  config.get("pop", "gamma.a.male"))
			self.gammaBMale = self.__find_resources( s_model_name,  config.get("pop", "gamma.b.male"))
			self.gammaAFemale = self.__find_resources( s_model_name,  config.get("pop", "gamma.a.female"))
			self.gammaBFemale = self.__find_resources( s_model_name,  config.get("pop", "gamma.b.female"))
			self.__update_attribute_config_file_info( "gammaAMale", "pop", "gamma.a.male" )
			self.__update_attribute_config_file_info( "gammaAFemale", "pop", "gamma.a.female" )
			self.__update_attribute_config_file_info( "gammaBMale", "pop", "gamma.b.male" )
			self.__update_attribute_config_file_info( "gammaBFemale", "pop", "gamma.b.female" )
		else:
			self.doNegBinom = False
	    #end if config.has gamma.b.male, then get all gammas
		#note that this def (sourced from Tiago's code) does not check for "doNegBinom",
		#but it is inferred from presence/absense of the gamma.b.male (as are all gamma{A,B} params)
		#but should be no harm in adding it to a written config file, where if won't be read
		#by this def:
		self.__update_attribute_config_file_info( "doNegBinom", "pop", "doNegBinom" )

		if config.has_option("pop", "survival"):
			self.survivalMale = self.__find_resources( s_model_name,  config.get("pop", "survival"))
			self.survivalFemale = self.__find_resources( s_model_name,  config.get("pop", "survival"))
		else:
			self.survivalMale = self.__find_resources( s_model_name,  config.get("pop", "survival.male"))
			self.survivalFemale = self.__find_resources( s_model_name,  config.get("pop", "survival.female"))
		#end if pop survival else not
		self.__update_attribute_config_file_info( "survivalMale", "pop", "survival.male" )
		self.__update_attribute_config_file_info( "survivalFemale", "pop", "survival.female" )


		self.fecundityMale = self.__find_resources( s_model_name,  config.get("pop", "fecundity.male"))
		self.__update_attribute_config_file_info( "fecundityMale", "pop", "fecundity.male" )
		self.fecundityFemale = self.__find_resources( s_model_name,  config.get("pop", "fecundity.female"))
		self.__update_attribute_config_file_info( "fecundityFemale", "pop", "fecundity.female" )

		if config.has_option("pop", "startLambda"):
			self.startLambda = config.getint("pop", "startLambda")
			self.lbd = config.getfloat("pop", "lambda")
			#self.lbd = mp.mpf(config.get("pop", "lambda"))
		else:
			self.startLambda = START_LAMBDA_IGNORE
			#self.lbd = mp.mpf(1.0)
			self.lbd = LAMBDA_IGNORE
		#end if startLambda, else not
		self.__update_attribute_config_file_info( "startLambda", "pop", "startLambda" )
		self.__update_attribute_config_file_info( "lbd", "pop", "lambda" )

		if config.has_option("pop", "Nb"):
			''''
			minimal change to Tiagos code so we can read in a "None" value
			for Nb, if such has been entered in config file. (Allows
			regularization of writing config files based on an input objects
			set of parameters)
			'''
			v_nb_val=eval( config.get( "pop", "Nb" ) ) 
			v_nbvar_val=eval(config.get("pop", "NbVar") )

			self.Nb = None if v_nb_val is None else config.getint("pop", "Nb")
			self.NbVar = None if v_nbvar_val is None else config.getfloat("pop", "NbVar")
		else:
			self.Nb = None
			self.NbVar = None
		#end if config has Nb, else not
		self.__update_attribute_config_file_info( "Nb", "pop", "Nb" )
		self.__update_attribute_config_file_info( "NbVar", "pop", "NbVar" )

		self.startAlleles = config.getint("genome", "startAlleles")
		self.__update_attribute_config_file_info( "startAlleles", "genome", "startAlleles" )

		self.mutFreq = config.getfloat("genome", "mutFreq")
		self.__update_attribute_config_file_info( "mutFreq", "genome", "mutFreq" )

		self.numMSats = config.getint("genome", "numMSats")
		self.__update_attribute_config_file_info( "numMSats", "genome", "numMSats" )

		if config.has_option("genome", "numSNPs"):
			self.numSNPs = config.getint("genome", "numSNPs")
		else:
			self.numSNPs = 0
		#end if config has numSNps else not
		self.__update_attribute_config_file_info( "numSnps", "genome", "numSnps" )

		self.reps = config.getint("sim", "reps")
		self.__update_attribute_config_file_info( "reps", "sim", "reps" )
		if config.has_option("sim", "startSave"):
			self.startSave = config.getint("sim", "startSave")
		else:
			self.startSave = 0
		#end if config has startSave
		self.__update_attribute_config_file_info( "startSave", "sim", "startSave" )

		self.gens = config.getint("sim", "gens")
		self.__update_attribute_config_file_info( "gens", "sim", "gens" )

		self.dataDir = config.get("sim", "dataDir")
		self.__update_attribute_config_file_info( "dataDir", "sim", "dataDir" )

		return
	#end __get_config

	def setupConfigParser( self, s_config_file_name ):
		self.config_file=os.path.basename( s_config_file_name )
		self.__make_config_parser( s_config_file_name )
		return
	#end setupResources  
	
	def getConfigParserOption( self, s_section_name, s_option_name ):
		s_val=None
		if self.__config_parser is not None:
			if self.__config_parser.has_section( s_section_name ):
				if self.__config_parser.has_option( s_section_name, s_option_name ):
					s_val = self.__config_parser.get( s_section_name, s_option_name )
				#end if has option
			#end if has section
		#end if parser
		return s_val
	#end getConfigOption

	def addParameter( self, s_attribute_name, v_attribute_value, 
			s_config_file_option_name, 
			s_config_file_section_name ):
		'''
		If user wants to add a parameter not in the current set of params as read
		in from the config file source of this instance, this def will both add the 
		param and value, plus update the member dictionaries that facilitate
		writing a new config file that includes this parameter.  Note that the
		arg s_config_file_option_name is necessitated by Tiago's standards in 
		his config files, as he often uses an attribute name different
		from the option name that gives the value.
		'''
		setattr( self, s_attribute_name, v_attribute_value )
		self.__update_attribute_config_file_info( s_attribute_name, s_config_file_section_name, 
				s_config_file_option_name )
		return
	#end addParameter

	def __get_configparser_input_params( self ):
		'''
		make a ConfigParser object using the current set of input parmater 
		attribute values, using the param_names member attribute to 
		to find the attribute names for the parameters used in the simupop
		simulation run
		'''

		if self.__param_names is None:
			s_msg="In PGInputSimuPop instance, can't write config file" \
					+ ": missing the required PGParamSet object."
			raise Exception( s_msg )
		#end if no parma set object

		o_parser=ConfigParser()
		o_parser.optionxform=str

		ls_attribute_names=self.param_names.shortnames

		for s_attribute in ls_attribute_names:
			if hasattr( self, s_attribute ): 
				#if this attribute was not in the original config file,
				#but was set in the GUI, we rely on the param_names
				#object (listing attribute names, their corresponding lable text,
				#and their section names (as part of the parma_names.tags), to provide
				#the section name, with which we update this input object:
				if s_attribute not in self.__config_file_section_name_by_attribute_name:
					s_new_entry_section=self.param_names.getConfigSectionNameForParam( s_attribute )
					#for config file sections, this will be all lower case:
					s_new_entry_section=s_new_entry_section.lower()

					#for this attribute we assume that the code from Tiago uses the same name
					#for the config file as is used in his original cfg object, now our self input object:
					self.__update_attribute_config_file_info( s_attribute, s_new_entry_section, s_attribute )
				#end if attribute was not registered in section dict (i.e. was not listed in the original
				#config file read in in def __get_config

				s_section_name=self.__config_file_section_name_by_attribute_name[ s_attribute ]
				s_option_name=self.__config_file_option_name_by_attribute_name[ s_attribute ]

				if s_section_name not in o_parser.sections():
					o_parser.add_section( s_section_name )
				#end if new section

				o_parser.set( s_section_name, s_option_name, getattr( self, s_attribute ) ) 
			#end if this instance has this attribute 
		#end for each attribue

		return o_parser
	#end __get_configparser_input_params

	def getDictParamValuesByAttributeName( self ):
		'''
		Note that this algorithm simply skips
		over paramters with names in the PGParamSet
		object, but without a corresponding attribute
		in this (self) instance.
		'''
		dv_param_values_by_name={}

		if self.__param_names is None:
			s_msg="In PGInputSimuPop instance, can't get dict of param/values" \
					+ ": missing the required PGParamSet object."
			raise Exception( s_msg )
		#end if no parma set object

		ls_attribute_names=self.param_names.shortnames

		for s_name in ls_attribute_names:
			if hasattr( self, s_name ):
				dv_param_values_by_name[ s_name ]=getattr( self, s_name )
			#end if hasattr
		#end for each param name
		
		return dv_param_values_by_name
	#end getDictParamValuesByAttributeName

	def writeInputParamsToFileObject( self, o_file ):

		o_parser=self.__get_configparser_input_params()
		o_parser.write( o_file )

		return
	#end writeInputParamsToFileObject

	def writeInputParamsAsConfigFile( self, s_outfile_name ):
		o_parser=self.__get_configparser_input_params()
		
		if os.path.isfile( s_outfile_name ):
			s_msg="In PGInputSimuPop instance, " \
						+ "can't write to file "  \
						+ s_outfile_name \
						+ ": file exists."
			raise Exception( s_msg  )
		#end if file exists

		o_file=open( s_outfile_name, 'w' )
		o_parser.write( o_file )
		o_file.close()
		return
	#end writeInputParamsAsConfigFile

	def makeInputConfig( self ):
		self.__get_config()
		self.__make_params_whose_values_are_lists_have_uniform_item_types()
		return
	#end makeInputConfig

	@property 
	def param_names( self ):
		return self.__param_names
	#end def paramnames

	@param_names.setter
	def param_names( self, o_param_names ):
		self.__param_names=o_param_names
		return
	#end paramnames

	def copyMe( self ):
		o_copy=PGInputSimuPop( self.__full_config_file_name,
				self.__resources,
				self.__param_names )

		#update input object with any param values
		#changed after reading in the config file
		#(for example, changed in the gui interface):
		dv_param_vals_by_name=self.getDictParamValuesByAttributeName()
		for s_param_name in dv_param_vals_by_name:
			setattr( o_copy, s_param_name, dv_param_vals_by_name[ s_param_name ] )
		#end for each param name

		return o_copy
	#end copyMe

	def __make_params_whose_values_are_lists_have_uniform_item_types( self ):

		'''
		Some lists as given in configuraion files have "0" entered as one item, 
		which the python's "eval" call evaluates as an int, while other items 
		in the lists have decimals, such as "32.2", which is evaluated as a float 
		type.  In these cases, in order to manage input by users, when
		this object is tied to a GUI, we want uniform types, and so will promote
		these ints to floats.  Note that as of 2016_09_20, we only correct his case.
		If we find paramaters (as given by our member PGParamSet object) with list
		as value, also having multi-types among its items, we will throw an exception.
		'''

		dv_param_vals_by_name=self.getDictParamValuesByAttributeName()

		for s_param_name in dv_param_vals_by_name:
			v_val=dv_param_vals_by_name[ s_param_name ]
			if type( v_val ) == list:

				di_types={ type( this_val ).__name__:1 for this_val in v_val }
				
				ls_types=list( di_types.keys() )
				ls_types.sort()
				if len( ls_types ) > 1:
					if ls_types==[ 'float','int' ]:
						setattr( self, s_param_name, [ float( i ) for i in v_val ] )
					else:
						s_msg="In PGInputSimuPop instance, " \
								+ "def __make_params_whose_values" \
								+ "_are_lists_have_uniform_item_types" \
								+ "the parameter " + s_param_name \
								+ "has more than one type.  The only valid " \
								+ "case of such lists is those with int and float " \
								+ "items.  This list, " + str( v_val ) \
								+ " , with types, " + str( lo_types ) + "."
						raise Exception( s_msg )
					#end if list is mix of ints and floats, make all floats, else error
				#end if non-uniqe types in list
			#end of attribute is a list
		#end for each param name
		return
	#end __make_params_whose_values_are_lists_have_uniform_item_types
#end class

if __name__ == "__main__":
	import sys
	import pgutilities as pgut
	import pgparamset as pgps
	import pgsimupopresources as pgsr	
	ls_args=[ "config file", "life-table file", "paramset file", "outfile_name" ]

	s_usage=pgut.do_usage_check( sys.argv, ls_args )

	if s_usage:
		print( s_usage )
		sys.exit()
	#end if usage

	s_configfile=sys.argv[1]
	s_lifetable=sys.argv[2]
	s_paramset=sys.argv[3]
	s_outfile=sys.argv[4]

	o_paramset=pgps.PGParamSet( s_paramset )
	o_lifetable=pgsr.PGSimuPopResources( [s_lifetable] )
	o_input=PGInputSimuPop( s_configfile, o_lifetable, o_paramset )
	o_input.makeInputConfig()
	o_input.writeInputParamsAsConfigFile( s_outfile )

#end if main

