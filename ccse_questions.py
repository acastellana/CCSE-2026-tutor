#!/usr/bin/env python3
"""
Extract CCSE questions and generate bilingual Spanish/Russian document
"""

# All questions with their correct answers
# Format: question_num: (spanish_question, spanish_answer)
questions = {
    # TAREA 1: Gobierno, legislación y participación ciudadana
    1001: ("España es…", "una monarquía parlamentaria."),
    1002: ("La ley fundamental de España se llama…", "Constitución."),
    1003: ("Según la Constitución española, la soberanía nacional reside en…", "el pueblo español."),
    1004: ("El Instituto de las Mujeres es…", "un organismo español."),
    1005: ("¿Cuándo puedo hacer los trámites en la sede electrónica?", "En cualquier horario."),
    1006: ("El castellano o español es lengua oficial…", "en toda España."),
    1007: ("¿Cuál de estas fuerzas de seguridad es de ámbito autonómico?", "Policía Foral de Navarra."),
    1008: ("¿Qué fuerza de seguridad está en toda España?", "El Cuerpo Nacional de Policía."),
    1009: ("En la Constitución se establece la separación de poderes: el poder ejecutivo, el legislativo y el…", "judicial."),
    1010: ("La bandera de España debe utilizarse…", "en todos los edificios públicos."),
    1011: ("¿Quién es el jefe del Estado en España?", "El rey."),
    1012: ("La gestión de la sanidad es competencia de…", "las comunidades autónomas."),
    1013: ("¿Quién fue el primer presidente del Gobierno de España en democracia?", "Adolfo Suárez."),
    1014: ("¿Cuál de estos organismos se encarga de interpretar la Constitución?", "El Tribunal Constitucional."),
    1015: ("¿Quién modera el funcionamiento de las instituciones españolas?", "El rey."),
    1016: ("¿Cómo se llama la cámara de representación territorial en España?", "Senado."),
    1017: ("¿Qué se necesita para hacer trámites por internet con la Administración?", "Una firma electrónica."),
    1018: ("¿Cómo se aprobó la Constitución?", "Por referéndum."),
    1019: ("¿Cómo se llama la ley más importante de cada comunidad autónoma?", "Estatuto de Autonomía."),
    1020: ("Las instalaciones culturales y deportivas públicas son competencia del…", "Ayuntamiento."),
    1021: ("¿Quién dirige la administración militar de España?", "El Gobierno."),
    1022: ("¿Qué hay en las Islas Baleares, en vez de diputaciones?", "Consejos insulares."),
    1023: ("¿Qué ciudad tiene más habitantes?", "Barcelona."),
    1024: ("Las Cortes Generales representan…", "al pueblo español."),
    1025: ("El Congreso de los Diputados y el Senado constituyen el poder…", "legislativo."),
    1026: ("¿Cómo pueden los ciudadanos proponer nuevas leyes al Congreso?", "Reuniendo 500 000 firmas."),
    1027: ("¿Cuántas comunidades autónomas hay en España?", "17."),
    1028: ("Los colores de la bandera española son…", "rojo y amarillo."),
    1029: ("¿Dónde está la sede del Gobierno de España?", "En Madrid."),
    1030: ("La bandera azul con 12 estrellas amarillas en círculo es la bandera de…", "la Unión Europea."),
    1031: ("En las elecciones municipales se vota a…", "alcaldes y concejales."),
    1032: ("¿Qué lengua es oficial en el País Vasco?", "El euskera."),
    1033: ("Todos los españoles tienen el deber de conocer la lengua…", "oficial del Estado."),
    1034: ("El aranés es una lengua cooficial que se habla en un pequeño territorio de…", "Cataluña."),
    1035: ("Las instituciones de una comunidad autónoma son: el consejo de gobierno, el presidente y…", "la asamblea legislativa."),
    1036: ("¿Cuál de estas opciones es una lengua cooficial en alguna comunidad autónoma?", "El gallego."),
    1037: ("¿Qué institución tiene como fin la promoción de la enseñanza de la lengua española y la difusión de la cultura en español?", "El Instituto Cervantes."),
    1038: ("¿Cuál de los siguientes organismos trabaja para conseguir la normalización lingüística?", "La Real Academia Española."),
    1039: ("¿Dónde vive el presidente del Gobierno?", "En el Palacio de la Moncloa."),
    1040: ("¿Cuál de los siguientes cuerpos forma parte de las Fuerzas Armadas de España?", "El Ejército del Aire."),
    1041: ("¿Quiénes forman parte del Gobierno?", "Los ministros."),
    1042: ("España es un…", "estado social y democrático de Derecho."),
    1043: ("¿Cuál de las siguientes siglas corresponde a un partido político?", "PP."),
    1044: ("¿Qué título tiene la futura reina, hija del rey?", "Princesa de Asturias."),
    1045: ("¿Con qué rey se restaura la democracia en España después del régimen de Franco?", "Con Juan Carlos I."),
    1046: ("¿En qué año se aprobó la Constitución española?", "En 1978."),
    1047: ("¿Cuántas comunidades autónomas tienen su propia bandera?", "Todas."),
    1048: ("¿Qué organismo oficial atiende las quejas de los ciudadanos por el mal funcionamiento de las administraciones?", "El Defensor del Pueblo."),
    1049: ("¿Cuántas firmas, como mínimo, deben recoger los ciudadanos para poder presentar una proposición de ley?", "500 000."),
    1050: ("¿A cuál de las siguientes organizaciones internacionales pertenece España?", "Fondo Monetario Internacional (FMI)."),
    1051: ("En la organización de la Administración se distinguen tres niveles: central, autonómica y…", "local."),
    1052: ("El poder legislativo corresponde...", "a los diputados y senadores."),
    1053: ("¿Dónde vive el rey?", "En el Palacio de la Zarzuela."),
    1054: ("El nombre oficial del parlamento español es…", "Cortes Generales."),
    1055: ("El Instituto de Comercio Exterior de España, el Instituto de las Mujeres y la Dirección General de Tráfico…", "dependen de ministerios."),
    1056: ("¿Quién puede reinar en España?", "Tanto los hombres como las mujeres."),
    1057: ("El Tribunal de Cuentas depende de…", "las Cortes Generales."),
    1058: ("¿Quién es la tercera autoridad del Estado, después del rey y el presidente del Gobierno?", "El presidente del Congreso de los Diputados."),
    1059: ("¿Qué lengua cooficial se habla en las Islas Baleares?", "Catalán."),
    1060: ("La Constitución defiende valores tales como la libertad, la igualdad, el pluralismo político y…", "la justicia."),
    1061: ("Cuando una ley ya está aprobada, ¿qué necesita para poder aplicarse?", "Normas que la desarrollen."),
    1062: ("¿Cuántos habitantes hay en España?", "49 millones."),
    1063: ("¿Cuál de estos es un órgano consultivo del Gobierno de España?", "El Consejo de Estado."),
    1064: ("¿Quién dirige la política interior y exterior de España?", "El Gobierno."),
    1065: ("El Defensor del Pueblo depende de…", "las Cortes Generales."),
    1066: ("El Instituto Etxepare tiene como misión la difusión del…", "euskera y la cultura vasca."),
    1067: ("¿Cuál de estas ciudades se encuentra entre las 10 más pobladas de España?", "Málaga."),
    1068: ("¿Quién puede realizar trámites en línea ante la Administración Pública?", "Cualquier ciudadano."),
    1069: ("¿Cómo se llama el rey de España?", "Felipe VI."),
    1070: ("¿Cómo se llama el órgano de gobierno de los jueces y magistrados?", "Consejo General del Poder Judicial."),
    1071: ("¿Quién aprueba los presupuestos generales del Estado?", "Las Cortes Generales."),
    1072: ("La Constitución española es…", "la ley fundamental."),
    1073: ("Las Cortes Generales están compuestas por el Senado y…", "el Congreso de los Diputados."),
    1074: ("¿Quién elabora las leyes?", "El poder legislativo."),
    1075: ("La defensa de la integridad territorial de España corresponde a…", "las Fuerzas Armadas."),
    1076: ("El Ejército español participa desde 1989 en misiones de paz de la…", "Organización de las Naciones Unidas (ONU)."),
    1077: ("¿Quién vigila puertos y aeropuertos, fronteras y costas?", "La Guardia Civil."),
    1078: ("¿Quién hace el control de pasaportes en las fronteras de España?", "La Policía Nacional."),
    1079: ("¿Cuál de los siguientes políticos ha sido presidente del Gobierno en España?", "José María Aznar."),
    1080: ("¿Cómo se llama la policía autonómica de Cataluña?", "Mossos d'Esquadra."),
    1081: ("¿Cómo se llama la policía autonómica del País Vasco?", "Ertzaintza."),
    1082: ("¿Desde qué año es rey Felipe VI?", "Desde 2014."),
    1083: ("¿Quién regula el tráfico en los pueblos y ciudades?", "La Policía Local."),
    1084: ("¿Quién puede presentar una queja al Defensor del Pueblo?", "Todos los ciudadanos, españoles o extranjeros."),
    1085: ("En España el voto en las elecciones es…", "un derecho."),
    1086: ("¿Quién vigila el tráfico en las carreteras?", "La Guardia Civil."),
    1087: ("¿Qué organismo se encarga de recaudar los impuestos?", "La Agencia Tributaria."),
    1088: ("¿Dónde se publican las leyes nacionales?", "En el Boletín Oficial del Estado (BOE)."),
    1089: ("¿Cómo se llaman los órganos de gobierno que solo existen en Canarias?", "Cabildos."),
    1090: ("¿Cuál de estos trámites administrativos puede realizarse en la sede electrónica?", "Pagar los impuestos."),
    1091: ("¿Cuál es el número de teléfono de información de la Administración General del Estado?", "060."),
    1092: ("España está organizada en…", "comunidades autónomas."),
    1093: ("¿Cuántos partidos políticos hay en España?", "Muchos."),
    1094: ("¿Dónde tiene lugar la investidura del presidente del Gobierno?", "En el Congreso de los Diputados."),
    1095: ("¿Quién tiene el mando supremo de las Fuerzas Armadas?", "El rey."),
    1096: ("¿Quién es el representante del Estado en una comunidad autónoma?", "El delegado del Gobierno."),
    1097: ("¿Cuántas provincias hay en España?", "50."),
    1098: ("La enseñanza de las lenguas cooficiales es competencia…", "de la comunidad autónoma."),
    1099: ("El poder ejecutivo corresponde…", "al Gobierno del Estado."),
    1100: ("¿Cuántas cámaras hay en el Parlamento español?", "Dos."),
    1101: ("El suministro de agua y el alumbrado de las ciudades es competencia de…", "el ayuntamiento."),
    1102: ("En materias como nacionalidad, inmigración, emigración o extranjería solo tiene competencia…", "el Estado."),
    1103: ("¿Cuántas mujeres han sido presidentas de Gobierno en España?", "Ninguna."),
    1104: ("Las relaciones internacionales son competencia de…", "el Estado."),
    1105: ("El Ayuntamiento está formado por el alcalde y…", "los concejales."),
    1106: ("¿Quiénes forman el gobierno de las comunidades autónomas?", "El presidente y los consejeros."),
    1107: ("¿Cuál es el órgano de gobierno en los municipios?", "El ayuntamiento."),
    1108: ("¿Cómo se llaman los órganos de gobierno de las provincias españolas?", "Diputaciones."),
    1109: ("¿Cuál es el órgano superior del poder ejecutivo?", "El Gobierno."),
    1110: ("El idioma español también se llama…", "castellano."),
    1111: ("¿A quiénes se elige en las elecciones al Parlamento Europeo?", "A los eurodiputados."),
    1112: ("Los españoles pueden votar a partir de los…", "18 años."),
    1113: ("Algunos ciudadanos extranjeros pueden votar en las elecciones…", "municipales."),
    1114: ("¿Quién controla la gestión financiera del Estado?", "El Tribunal de Cuentas."),
    1115: ("¿A quiénes se elige en las elecciones generales?", "A los senadores y diputados."),
    1116: ("¿Cuántos miembros tiene el Congreso de los Diputados?", "350."),
    1117: ("Los municipios y provincias forman parte de la Administración…", "local."),
    1118: ("La comunidad autónoma más poblada de España es…", "Andalucía."),
    1119: ("¿Cómo se llama la organización que defiende los intereses de los trabajadores?", "Sindicato."),
    1120: ("¿Quién elige al presidente del Gobierno?", "El Congreso de los Diputados."),

    # TAREA 2: Derechos y deberes fundamentales
    2001: ("En España, la Constitución obliga a todos los ciudadanos a practicar una religión.", "Falso."),
    2002: ("Los españoles que obtienen la nacionalidad por residencia deben esperar tres años para poder votar en las elecciones.", "Falso."),
    2003: ("En España, la Constitución prohíbe la tortura y la pena de muerte.", "Verdadero."),
    2004: ("El funcionamiento de los partidos políticos tiene que ser democrático.", "Verdadero."),
    2005: ("Se puede obligar a alguien a decir cuáles son sus ideas políticas o religiosas.", "Falso."),
    2006: ("Se puede limitar a una persona el derecho a entrar y salir libremente de España por motivos ideológicos.", "Falso."),
    2007: ("La Educación Primaria (de 6 a 12 años) es gratuita y obligatoria.", "Verdadero."),
    2008: ("La Constitución garantiza el derecho de los españoles a una vivienda digna.", "Verdadero."),
    2009: ("En España la policía puede entrar en cualquier casa sin resolución judicial en cualquier momento.", "Falso."),
    2010: ("Se garantiza el secreto de las comunicaciones de los españoles, salvo resolución judicial.", "Verdadero."),
    2011: ("La Constitución reconoce el derecho de los ciudadanos a asociarse libremente.", "Verdadero."),
    2012: ("Los profesores pueden enseñar con libertad, dentro de los límites de la Constitución.", "Verdadero."),
    2013: ("La Constitución reconoce únicamente los derechos fundamentales de los españoles.", "Falso."),
    2014: ("Los ciudadanos deben colaborar con los jueces si se lo piden.", "Verdadero."),
    2015: ("La ley limita el acceso de terceras personas a datos de carácter personal.", "Verdadero."),
    2016: ("La libertad de prensa está limitada por el respeto al honor de las personas.", "Verdadero."),
    2017: ("En España las causas de separación y divorcio están reguladas por la ley.", "Verdadero."),
    2018: ("La atención sanitaria gratuita es solo para personas mayores de 65 años.", "Falso."),
    2019: ("En España los hombres y las mujeres tienen los mismos derechos.", "Verdadero."),
    2020: ("La enseñanza obligatoria consta de dos etapas: Educación Primaria y Educación Secundaria Obligatoria.", "Verdadero."),
    2021: ("En España hay una religión oficial.", "Falso."),
    2022: ("La atención sanitaria pública es gratuita.", "Verdadero."),
    2023: ("La enseñanza básica en España es solo para los extranjeros.", "Falso."),
    2024: ("En España está reconocido el derecho de asociación.", "Verdadero."),
    2025: ("Los sindicatos pueden participar en negociaciones con empresarios y con el Gobierno.", "Verdadero."),
    2026: ("Los trabajadores tienen derecho a hacer huelga.", "Verdadero."),
    2027: ("La libertad ideológica está garantizada solo en parte del territorio nacional.", "Falso."),
    2028: ("Todos los ciudadanos tienen acceso al sistema de Seguridad Social público, excepto si están desempleados.", "Falso."),
    2029: ("Todos tienen derecho a disfrutar de un medio ambiente adecuado para el desarrollo de la persona, así como el deber de conservarlo.", "Verdadero."),
    2030: ("En España, los poderes públicos deben proteger la salud y promover el deporte.", "Verdadero."),
    2031: ("La enseñanza básica en España es obligatoria y gratuita.", "Verdadero."),
    2032: ("La ley prohíbe la discriminación por cualquier circunstancia personal o social.", "Verdadero."),
    2033: ("En España, los ciudadanos pueden desplazarse libremente por todo el territorio nacional.", "Verdadero."),
    2034: ("Los jueces administran la justicia en España según las indicaciones del Gobierno.", "Falso."),
    2035: ("Los españoles deben ayudar en los casos de catástrofe o calamidad pública.", "Verdadero."),
    2036: ("En España los ciudadanos pueden elegir en qué ciudad quieren vivir.", "Verdadero."),

    # TAREA 3: Organización territorial de España. Geografía física y política
    3001: ("¿Dónde están Cáceres y Badajoz?", "En Extremadura."),
    3002: ("¿Cuál es la capital la Comunidad Valenciana?", "Valencia."),
    3003: ("¿Dónde están las islas Baleares?", "En el mar Mediterráneo."),
    3004: ("¿Cómo se llama la extensa llanura situada en el centro de la península ibérica?", "Meseta."),
    3005: ("El parque nacional de Ordesa está en...", "Aragón."),
    3006: ("¿En qué comunidad autónoma están Guadalajara y Cuenca?", "En Castilla-La Mancha."),
    3007: ("¿Qué comunidad autónoma tiene como capital Santiago de Compostela?", "Galicia."),
    3008: ("¿Dónde está Almería?", "En Andalucía."),
    3009: ("La capital de la comunidad autónoma de Galicia es…", "Santiago de Compostela."),
    3010: ("¿Cuál de estos ríos desemboca en el mar Mediterráneo?", "El Júcar."),
    3011: ("¿Dónde está el monte Aneto?", "En los Pirineos."),
    3012: ("La ciudad de Vitoria es la sede administrativa de…", "País Vasco."),
    3013: ("España se divide en…", "comunidades y ciudades autónomas."),
    3014: ("El parque nacional de Aigüestortes está en...", "Cataluña."),
    3015: ("En el norte de África están Ceuta y…", "Melilla."),
    3016: ("¿En qué lugar de España hay un clima que se caracteriza por inviernos fríos y veranos muy calurosos?", "Madrid."),
    3017: ("¿Cuál de estos ríos desemboca en el océano Atlántico?", "El Guadalquivir."),
    3018: ("¿Cuál de estas provincias forma parte de la Comunidad de Castilla y León?", "Burgos."),
    3019: ("¿En qué comunidad autónoma está la ciudad de Huesca?", "Aragón."),
    3020: ("Canarias tiene un clima…", "subtropical."),
    3021: ("El principal río que desemboca en el mar Mediterráneo es el…", "Ebro."),
    3022: ("España está entre los países de Europa más…", "montañosos."),
    3023: ("¿En qué provincia está el parque nacional de Monfragüe?", "En Cáceres."),
    3024: ("¿Cuál es la capital de la comunidad autónoma de Extremadura?", "Mérida."),

    # TAREA 4: Cultura e historia de España
    4001: ("Los personajes principales de la novela el Quijote son don Quijote y…", "Sancho Panza."),
    4002: ("¿Qué científica española es reconocida por sus investigaciones?", "Margarita Salas."),
    4003: ("¿Quién escribió La casa de Bernarda Alba?", "Federico García Lorca."),
    4004: ("¿Quién escribió Nada, una novela sobre la posguerra española?", "Carmen Laforet."),
    4005: ("¿Qué músico compuso El amor brujo?", "Manuel de Falla."),
    4006: ("¿Qué es típico en la Noche de San Juan?", "Encender hogueras."),
    4007: ("¿Cuál es el instrumento más característico de la música flamenca?", "La guitarra."),
    4008: ("Isabel Coixet es una…", "directora de cine."),
    4009: ("Una de las cantantes españolas más famosas actualmente es...", "Rosalía."),
    4010: ("¿En qué ciudad de España hay una mezquita que es Patrimonio de la Humanidad?", "Córdoba."),
    4011: ("¿En qué ciudad de España se encuentra La Alhambra, que es Patrimonio de la Humanidad?", "En Granada."),
    4012: ("¿Cuál es el nombre de la directora española que ha destacado por su mirada crítica y por modernizar el cine nacional?", "Pilar Miró."),
    4013: ("¿Qué novela de éxito ha escrito Irene Vallejo?", "El infinito en un junco."),
    4014: ("¿Cómo se llama la mayor institución pública dedicada a la investigación en España?", "Consejo Superior de investigaciones Científicas (CSIC)."),
    4015: ("Paco de Lucía fue un famoso….", "guitarrista."),
    4016: ("¿Qué celebramos el 24 de diciembre?", "Nochebuena."),
    4017: ("Juan Mari Arzak es un famoso....", "cocinero."),
    4018: ("¿Quién fue Clara Campoamor?", "Una defensora de los derechos de la mujer."),
    4019: ("¿Qué canciones típicas se cantan en Navidad?", "Villancicos."),
    4020: ("La Liga y la Copa del Rey son competiciones de…", "fútbol."),
    4021: ("¿Quién ha recibido el premio Nobel de Literatura?", "Vicente Aleixandre."),
    4022: ("¿Qué fiesta se celebra en Pamplona el 7 de julio?", "Los sanfermines."),
    4023: ("Teresa Perales y Daniel Molina son...", "campeones paraolímpicos."),
    4024: ("¿Qué toman los españoles la noche del 31 de diciembre para celebrar el cambio de año?", "Uvas."),
    4025: ("¿Qué mujer es autora del cuadro La verbena?", "Maruja Mallo."),
    4026: ("¿En qué museo español puedes ver el cuadro Guernica de Picasso?", "Museo Reina Sofía."),
    4027: ("¿Qué escritora española escribe en otra lengua oficial de España?", "Mercè Rodoreda."),
    4028: ("¿Qué tres culturas convivieron en la España medieval?", "La cristiana, la judía y la musulmana."),
    4029: ("El 6 de diciembre se celebra en España…", "el Día de la Constitución."),
    4030: ("¿Qué ciudad fue un centro científico en Al-Ándalus, donde se estudiaba medicina y astronomía?", "Córdoba."),
    4031: ("¿En qué ciudad española está el Museo Guggenheim?", "Bilbao."),
    4032: ("El Premio Cervantes se da a…", "escritores."),
    4033: ("¿Qué premio reconoce a los mejores actores y películas?", "Premio Goya."),
    4034: ("¿Qué premios promueven en España valores científicos, culturales y humanísticos?", "Los Premios Princesa de Asturias."),
    4035: ("¿Cuál de estos deportes es muy popular en España?", "El fútbol."),
    4036: ("¿Cuál de estos deportistas juega al tenis?", "Carlos Alcaraz."),

    # TAREA 5: Sociedad española
    5001: ("¿Qué documento deben solicitar los extranjeros para residir legalmente en España?", "La Tarjeta de Identidad de Extranjero (TIE)."),
    5002: ("¿Cuál es el documento que certifica el lugar de residencia del titular?", "El certificado de empadronamiento."),
    5003: ("¿A qué sustituye el registro electrónico individual?", "Al libro de familia."),
    5004: ("¿Cuál es la edad mínima para conducir un coche en España?", "18 años."),
    5005: ("El carné de conducir se hace en…", "la Dirección General de Tráfico (DGT)."),
    5006: ("Para sacar el carné de conducir hay que aprobar…", "un examen teórico y otro práctico."),
    5007: ("¿Dónde se tramita el libro de familia?", "En el Registro Civil."),
    5008: ("¿Cuál de estos canales de televisión es autonómico?", "Canal Sur."),
    5009: ("¿Cuánto dura el permiso de maternidad o paternidad?", "16 semanas."),
    5010: ("¿Cuál es la tasa máxima de alcohol en sangre permitida a los conductores, en gramos por litro (g/l)?", "0,5."),
    5011: ("¿Cuál es el tipo de residencia más habitual en España?", "Piso en un edificio de viviendas."),
    5012: ("¿Qué comunidad autónoma es conocida por la calidad de su aceite de oliva?", "Andalucía."),
    5013: ("¿Cómo se llama la revisión que deben pasar obligatoriamente los coches?", "ITV (Inspección Técnica de Vehículos)."),
    5014: ("El aperitivo que acompaña a la bebida en bares y restaurantes se llama...", "tapa."),
    5015: ("¿Dónde se tramita la tarjeta sanitaria?", "En el centro de salud."),
    5016: ("¿Con cuántos hijos una familia es numerosa?", "Con 3 hijos."),
    5017: ("En España está permitido el matrimonio…", "entre personas del mismo y diferente sexo."),
    5018: ("Los propietarios de perros deben registrarlos en…", "el Ayuntamiento."),
    5019: ("Los principales ingredientes de la tortilla española son huevos y…", "patatas."),
    5020: ("¿Cuál es uno de los platos más conocidos internacionalmente de la gastronomía española?", "Gazpacho."),
    5021: ("¿Cuál de estos canales de televisión es público?", "La 1."),
    5022: ("En una comunidad de vecinos, una de las normas es…", "no molestar con ruido."),
    5023: ("¿Cuál de estos es el principal ingrediente de la paella valenciana?", "Arroz."),
    5024: ("La sidra es una bebida típica de…", "Asturias."),
    5025: ("Los españoles tienen dos apellidos, el primero es…", "puede ser el de la madre o el del padre."),
    5026: ("La Fiesta Nacional de España es el…", "12 de octubre."),
    5027: ("¿Qué días suelen cerrar la mayoría de las tiendas o el pequeño comercio?", "Los domingos."),
    5028: ("¿Dónde se hace el pasaporte?", "En una comisaría de policía."),
    5029: ("El Ministerio de Igualdad es el encargado de luchar contra la violencia de género y la…", "discriminación."),
    5030: ("¿Qué comunidad autónoma es conocida por la calidad de sus cavas?", "Cataluña."),
    5031: ("¿Qué documento se necesita para recibir atención médica en la sanidad pública?", "La tarjeta sanitaria."),
    5032: ("El horario de Canarias, con respecto a la Península, es de…", "una hora menos."),
    5033: ("Para acceder a la Universidad se debe superar una prueba de evaluación llamada…", "Prueba de Acceso a la Universidad."),
    5034: ("¿Cuál de estos productos necesita importar España de otros países?", "Petróleo."),
    5035: ("¿Qué tipo de impuestos tienen que pagar los ciudadanos en España?", "Impuestos directos e indirectos."),
    5036: ("Los adultos sin Bachillerato pueden estudiar en la Universidad haciendo una prueba especial a partir de los…", "25 años."),
    5037: ("¿Dónde puede encontrarse la siguiente norma «No pisar el césped, ni arrancar flores»?", "En zonas de recreo."),
    5038: ("El Bachillerato en España…", "se compone de dos cursos académicos."),
    5039: ("El Impuesto sobre el Valor Añadido (IVA) forma parte de los…", "Impuestos indirectos."),
    5040: ("¿Qué número reciben los trabajadores al comenzar su primer empleo?", "El de la Seguridad Social."),
    5041: ("Los colegios públicos…", "son gratuitos."),
    5042: ("¿Cuál de estos puertos es uno de los principales de España?", "Algeciras."),
    5043: ("Un colegio concertado es un colegio privado que…", "recibe dinero de la Administración."),
    5044: ("España exporta productos principalmente a países…", "de la Unión Europea."),
    5045: ("Las bibliotecas públicas son gratuitas para…", "todos."),
    5046: ("¿Cuál de estos productos exporta España más que importa?", "Calzado."),
    5047: ("Una persona mayor de 18 años puede obtener el título de Graduado en Educación Secundaria Obligatoria en…", "un Centro de Educación de Personas Adultas."),
    5048: ("La formación profesional…", "puede ser de grado medio o superior."),
    5049: ("¿Adónde vamos para ver al médico de familia o al pediatra?", "Al centro de salud."),
    5050: ("¿Para cuántos años vale la tarjeta sanitaria europea?", "Para dos años."),
    5051: ("¿A qué hora se cena normalmente en España?", "A las 21 o 22 h."),
    5052: ("¿Cuál es el número de teléfono único para cualquier emergencia?", "112."),
    5053: ("¿Cuál de estos periódicos se publica a nivel nacional?", "El País."),
    5054: ("¿Dónde se venden sellos y tabaco?", "En el estanco."),
    5055: ("¿Cuándo se puede llamar al número de teléfono para atención a víctimas de violencia de género?", "Las 24 horas del día."),
    5056: ("La organización que trabaja para conseguir la integración de las personas con discapacidad visual es…", "la ONCE."),
    5057: ("El Camino de Santiago es…", "Patrimonio de la Humanidad."),
    5058: ("¿Cuál es el canal de televisión estatal que transmite noticias de actualidad nacional e internacional continuamente?", "Canal 24 horas."),
    5059: ("El teléfono gratuito para las víctimas de violencia de género es el…", "016."),
    5060: ("En España, la red de trenes puede ser de larga distancia, de media distancia y…", "de cercanías."),
    5061: ("¿Qué está prohibido en la puerta de un colegio?", "Fumar un cigarrillo."),
    5062: ("¿Qué título se obtiene al finalizar un ciclo de grado medio de Formación Profesional?", "Técnico."),
    5063: ("¿Qué título se obtiene tras realizar una tesis doctoral en España?", "Doctor."),
    5064: ("¿Dónde se compran las medicinas con receta?", "En la farmacia."),
    5065: ("¿Cuál de estas tres recomendaciones podemos encontrar en un parque?", "No pisar el césped."),
    5066: ("¿Cuál de las siguientes cosas es obligatoria para el propietario de un coche en España?", "El seguro."),
    5067: ("El aeropuerto Adolfo Suárez está en…", "Madrid."),
    5068: ("En un coche es obligatorio el uso del cinturón de seguridad...", "en todos los asientos."),
    5069: ("¿Cuál es el límite de velocidad en autopista?", "120 km/h."),
    5070: ("Ceder el asiento a las personas con movilidad reducida es una norma que encontramos indicada en…", "el transporte público."),
    5071: ("¿Cuál es el medio de transporte público que tiene una luz verde encendida si está libre?", "El taxi."),
    5072: ("¿Qué debes hacer si tienes un perro?", "Ponerle un microchip y vacunarlo."),
    5073: ("Los españoles necesitan el pasaporte para viajar a…", "China."),
    5074: ("¿Cuál es la edad mínima para trabajar en España?", "16 años."),
    5075: ("¿Cuál es el sector de mayor peso en la economía española?", "Servicios."),
    5076: ("España es innovadora en el sector de…", "las energías renovables."),
    5077: ("¿Cómo se llama la ley laboral más importante de España?", "El Estatuto de los Trabajadores."),
    5078: ("¿Cuál de estos establecimientos está abierto 24 horas si es necesario?", "Farmacia."),
    5079: ("La educación infantil en España…", "tiene dos ciclos."),
    5080: ("¿Cuándo empieza el calendario escolar?", "En septiembre."),
    5081: ("Las Escuelas Oficiales de Idiomas…", "son para mayores de 16 años."),
    5082: ("¿Cuál es el documento que recoge los años de cotización a la Seguridad Social?", "Informe de vida laboral."),
    5083: ("Los convenios colectivos de una empresa son los que se firman con los representantes de los trabajadores sobre…", "las condiciones laborales."),
    5084: ("¿En cuál de estos sectores destaca España?", "En el turismo."),
}

# Russian translations

translations = {
    1001: {
        "question": 'Испания — это…',
        "answer": 'парламентская монархия.',
        "options": [
            {"label": 'a', "text": 'парламентская монархия.'},
            {"label": 'b', "text": 'федеративная республика.'},
            {"label": 'c', "text": 'федеральная монархия.'},
        ],
    },
    1002: {
        "question": 'Основной закон Испании называется…',
        "answer": 'Конституция.',
        "options": [
            {"label": 'a', "text": 'Конституция.'},
            {"label": 'b', "text": 'Основной закон.'},
            {"label": 'c', "text": 'Основное упорядочение.'},
        ],
    },
    1003: {
        "question": 'Согласно Конституции Испании, национальный суверенитет принадлежит…',
        "answer": 'испанскому народу.',
        "options": [
            {"label": 'a', "text": 'испанский народ'},
            {"label": 'b', "text": 'Государственное правительство.'},
            {"label": 'c', "text": 'Конгресс депутатов.'},
        ],
    },
    1004: {
        "question": 'Институт женщин — это…',
        "answer": 'испанский государственный орган.',
        "options": [
            {"label": 'a', "text": 'европейская институция.'},
            {"label": 'b', "text": 'испанский орган.'},
            {"label": 'c', "text": 'некоммерческая организация (НКО)'},
        ],
    },
    1005: {
        "question": 'Когда можно совершать административные процедуры на электронном портале?',
        "answer": 'В любое время.',
        "options": [
            {"label": 'a', "text": 'В любое время.'},
            {"label": 'b', "text": 'Только утром.'},
            {"label": 'c', "text": 'С понедельника по пятницу.'},
        ],
    },
    1006: {
        "question": 'Кастильский или испанский язык является официальным…',
        "answer": 'на всей территории Испании.',
        "options": [
            {"label": 'a', "text": 'по всей Испании.'},
            {"label": 'b', "text": 'только там, где нет других языков.'},
            {"label": 'c', "text": 'на всей Иберийском полуострове.'},
        ],
    },
    1007: {
        "question": 'Какая из этих сил безопасности является региональной?',
        "answer": 'Форальная полиция Наварры.',
        "options": [
            {"label": 'a', "text": 'Местная полиция.'},
            {"label": 'b', "text": 'Гражданская гвардия.'},
            {"label": 'c', "text": 'Полиция Форал де Наварра.'},
        ],
    },
    1008: {
        "question": 'Какая служба безопасности работает по всей Испании?',
        "answer": 'Национальный полицейский корпус.',
        "options": [
            {"label": 'a', "text": 'Полиция Форал de Наварра.'},
            {"label": 'b', "text": 'Национальная полиция.'},
            {"label": 'c', "text": "Моссос д'Эсквадра."},
        ],
    },
    1009: {
        "question": 'В Конституции установлено разделение властей: исполнительная, законодательная и…',
        "answer": 'судебная.',
        "options": [
            {"label": 'a', "text": 'судебный'},
            {"label": 'b', "text": 'информационный'},
            {"label": 'c', "text": 'политик'},
        ],
    },
    1010: {
        "question": 'Флаг Испании должен использоваться…',
        "answer": 'на всех государственных зданиях.',
        "options": [
            {"label": 'a', "text": 'только в официальные праздничные дни.'},
            {"label": 'b', "text": 'во всех государственных зданиях.'},
            {"label": 'c', "text": 'только в актах испанского правительства.'},
        ],
    },
    1011: {
        "question": 'Кто является главой государства в Испании?',
        "answer": 'Король.',
        "options": [
            {"label": 'a', "text": 'Президент правительства.'},
            {"label": 'b', "text": 'Король.'},
            {"label": 'c', "text": 'Министр экономики.'},
        ],
    },
    1012: {
        "question": 'Управление здравоохранением относится к компетенции…',
        "answer": 'автономных сообществ.',
        "options": [
            {"label": 'a', "text": 'государство.'},
            {"label": 'b', "text": 'автономные сообщества'},
            {"label": 'c', "text": 'муниципалитеты'},
        ],
    },
    1013: {
        "question": 'Кто был первым председателем правительства демократической Испании?',
        "answer": 'Адольфо Суарес.',
        "options": [
            {"label": 'a', "text": 'Мариано Рахой.'},
            {"label": 'b', "text": 'Адольфо Суарес.'},
            {"label": 'c', "text": 'Хосе Луис Родригес Сапатеро.'},
        ],
    },
    1014: {
        "question": 'Какой из этих органов занимается толкованием Конституции?',
        "answer": 'Конституционный суд.',
        "options": [
            {"label": 'a', "text": 'Конституционная власть.'},
            {"label": 'b', "text": 'Конституционный суд.'},
            {"label": 'c', "text": 'Совет генерального судебного управления.'},
        ],
    },
    1015: {
        "question": 'Кто регулирует деятельность испанских институтов?',
        "answer": 'Король.',
        "options": [
            {"label": 'a', "text": 'Президент правительства.'},
            {"label": 'b', "text": 'Король.'},
            {"label": 'c', "text": 'Директор Королевской академии испанского языка.'},
        ],
    },
    1016: {
        "question": 'Как называется палата территориального представительства в Испании?',
        "answer": 'Сенат.',
        "options": [
            {"label": 'a', "text": 'Сенат.'},
            {"label": 'b', "text": 'Постоянная комиссия.'},
            {"label": 'c', "text": 'Конгресс депутатов.'},
        ],
    },
    1017: {
        "question": 'Что нужно для совершения административных процедур через интернет?',
        "answer": 'Электронная подпись.',
        "options": [
            {"label": 'a', "text": 'Действительный паспорт.'},
            {"label": 'b', "text": 'Электронная подпись.'},
            {"label": 'c', "text": 'Подпись на бумаге.'},
        ],
    },
    1018: {
        "question": 'Как была принята Конституция?',
        "answer": 'Путём референдума.',
        "options": [
            {"label": 'a', "text": 'По юридическому требованию.'},
            {"label": 'b', "text": 'По референдуму.'},
            {"label": 'c', "text": 'По Конституционному суду.'},
        ],
    },
    1019: {
        "question": 'Как называется главный закон каждого автономного сообщества?',
        "answer": 'Статут автономии.',
        "options": [
            {"label": 'a', "text": 'Статут автономии.'},
            {"label": 'b', "text": 'Автономное законодательство.'},
            {"label": 'c', "text": 'Закон сообщества.'},
        ],
    },
    1020: {
        "question": 'Культурные и спортивные объекты общественного пользования находятся в ведении…',
        "answer": 'муниципалитета.',
        "options": [
            {"label": 'a', "text": 'Городской совет.'},
            {"label": 'b', "text": 'Министерство образования, профессионального обучения и спорта.'},
            {"label": 'c', "text": 'Министерство равенства.'},
        ],
    },
    1021: {
        "question": 'Кто руководит военной администрацией Испании?',
        "answer": 'Правительство.',
        "options": [
            {"label": 'a', "text": 'Муниципалитеты.'},
            {"label": 'b', "text": 'Правительство.'},
            {"label": 'c', "text": 'Генеральные Кортесы.'},
        ],
    },
    1022: {
        "question": 'Что есть на Балеарских островах вместо провинциальных советов?',
        "answer": 'Островные советы.',
        "options": [
            {"label": 'a', "text": 'Кабильдос.'},
            {"label": 'b', "text": 'Островные советы.'},
            {"label": 'c', "text": 'Центры депутатов.'},
        ],
    },
    1023: {
        "question": 'В каком городе больше жителей?',
        "answer": 'Барселона.',
        "options": [
            {"label": 'a', "text": 'Севилья.'},
            {"label": 'b', "text": 'Барселона.'},
            {"label": 'c', "text": 'Сарагоса.'},
        ],
    },
    1024: {
        "question": 'Генеральные кортесы представляют…',
        "answer": 'испанский народ.',
        "options": [
            {"label": 'a', "text": 'народу Испании.'},
            {"label": 'b', "text": 'к политическим партиям.'},
            {"label": 'c', "text": 'к министрам.'},
        ],
    },
    1025: {
        "question": 'Конгресс депутатов и Сенат составляют…власть.',
        "answer": 'законодательную.',
        "options": [
            {"label": 'a', "text": 'исполнительный'},
            {"label": 'b', "text": 'законодательный'},
            {"label": 'c', "text": 'судебный'},
        ],
    },
    1026: {
        "question": 'Как граждане могут предложить новые законы Конгрессу?',
        "answer": 'Собрав 500 000 подписей.',
        "options": [
            {"label": 'a', "text": 'Собирая 500 000 подписей.'},
            {"label": 'b', "text": 'Прося короля.'},
            {"label": 'c', "text": 'Создание ассоциации.'},
        ],
    },
    1027: {
        "question": 'Сколько автономных сообществ в Испании?',
        "answer": '17.',
        "options": [
            {"label": 'a', "text": '8.'},
            {"label": 'b', "text": '17.'},
            {"label": 'c', "text": '25.'},
        ],
    },
    1028: {
        "question": 'Цвета испанского флага…',
        "answer": 'красный и жёлтый.',
        "options": [
            {"label": 'a', "text": 'белый и красный.'},
            {"label": 'b', "text": 'красный и желтый.'},
            {"label": 'c', "text": 'желтый и белый.'},
        ],
    },
    1029: {
        "question": 'Где находится резиденция правительства Испании?',
        "answer": 'В Мадриде.',
        "options": [
            {"label": 'a', "text": 'В Мадриде.'},
            {"label": 'b', "text": 'В Барселоне.'},
            {"label": 'c', "text": 'В Севилье.'},
        ],
    },
    1030: {
        "question": 'Синий флаг с 12 жёлтыми звёздами по кругу — это флаг…',
        "answer": 'Европейского союза.',
        "options": [
            {"label": 'a', "text": 'Европейский Союз.'},
            {"label": 'b', "text": 'Европейский парламент.'},
            {"label": 'c', "text": 'Европейская комиссия.'},
        ],
    },
    1031: {
        "question": 'На муниципальных выборах голосуют за…',
        "answer": 'мэров и членов муниципального совета.',
        "options": [
            {"label": 'a', "text": 'мэры и советники'},
            {"label": 'b', "text": 'министры и министрши.'},
            {"label": 'c', "text": 'депутаты и сенаторы.'},
        ],
    },
    1032: {
        "question": 'Какой язык является официальным в Стране Басков?',
        "answer": 'Баскский (эускера).',
        "options": [
            {"label": 'a', "text": 'Бабле.'},
            {"label": 'b', "text": 'арагонский'},
            {"label": 'c', "text": 'Баскский язык.'},
        ],
    },
    1033: {
        "question": 'Все испанцы обязаны знать…язык.',
        "answer": 'официальный государственный.',
        "options": [
            {"label": 'a', "text": 'автономная от государства.'},
            {"label": 'b', "text": 'государственный служащий'},
            {"label": 'c', "text": 'местное государственное учреждение.'},
        ],
    },
    1034: {
        "question": 'Аранский язык — это соофициальный язык, на котором говорят в небольшой части…',
        "answer": 'Каталонии.',
        "options": [
            {"label": 'a', "text": 'Каталония.'},
            {"label": 'b', "text": 'Ла Риоха.'},
            {"label": 'c', "text": 'Арагон.'},
        ],
    },
    1035: {
        "question": 'Институты автономного сообщества: совет правительства, президент и…',
        "answer": 'законодательная ассамблея.',
        "options": [
            {"label": 'a', "text": 'муниципалитет'},
            {"label": 'b', "text": 'законодательное собрание'},
            {"label": 'c', "text": 'делегация правительства'},
        ],
    },
    1036: {
        "question": 'Какой из этих языков является соофициальным в каком-либо автономном сообществе?',
        "answer": 'Галисийский.',
        "options": [
            {"label": 'a', "text": 'Галисиец.'},
            {"label": 'b', "text": 'Арагонский.'},
            {"label": 'c', "text": 'Мурсианец.'},
        ],
    },
    1037: {
        "question": 'Какое учреждение занимается распространением испанского языка и культуры?',
        "answer": 'Институт Сервантеса.',
        "options": [
            {"label": 'a', "text": 'Национальный институт государственной администрации.'},
            {"label": 'b', "text": 'Национальный институт статистики.'},
            {"label": 'c', "text": 'Институт Сервантеса.'},
        ],
    },
    1038: {
        "question": 'Какая из следующих организаций работает над языковой нормализацией?',
        "answer": 'Королевская академия испанского языка.',
        "options": [
            {"label": 'a', "text": 'Институт Рамона Ллулла.'},
            {"label": 'b', "text": 'Институт Сервантеса.'},
            {"label": 'c', "text": 'Королевская академия испанского языка.'},
        ],
    },
    1039: {
        "question": 'Где живёт председатель правительства?',
        "answer": 'Во дворце Монклоа.',
        "options": [
            {"label": 'a', "text": 'В Королевском дворце.'},
            {"label": 'b', "text": 'В дворце Сарсуэла.'},
            {"label": 'c', "text": 'В Дворце Монклоа.'},
        ],
    },
    1040: {
        "question": 'Какой из следующих корпусов входит в состав Вооружённых сил Испании?',
        "answer": 'Военно-воздушные силы.',
        "options": [
            {"label": 'a', "text": 'Форальная полиция.'},
            {"label": 'b', "text": 'Гражданская гвардия.'},
            {"label": 'c', "text": 'Военно-воздушные силы.'},
        ],
    },
    1041: {
        "question": 'Кто входит в состав правительства?',
        "answer": 'Министры.',
        "options": [
            {"label": 'a', "text": 'Министры.'},
            {"label": 'b', "text": 'советники'},
            {"label": 'c', "text": 'Мэры.'},
        ],
    },
    1042: {
        "question": 'Испания — это…',
        "answer": 'социальное и демократическое правовое государство.',
        "options": [
            {"label": 'a', "text": 'социальное и демократическое правовое государство.'},
            {"label": 'b', "text": 'свободное ассоциированное государство'},
            {"label": 'c', "text": 'конфедеративное государство'},
        ],
    },
    1043: {
        "question": 'Какая из следующих аббревиатур соответствует политической партии?',
        "answer": 'PP (Народная партия).',
        "options": [
            {"label": 'a', "text": 'ПП.'},
            {"label": 'b', "text": 'ВВП.'},
            {"label": 'c', "text": 'ЕС.'},
        ],
    },
    1044: {
        "question": 'Какой титул носит будущая королева, дочь короля?',
        "answer": 'Принцесса Астурийская.',
        "options": [
            {"label": 'a', "text": 'Принцесса Астурийская.'},
            {"label": 'b', "text": 'Принцесса Арагона.'},
            {"label": 'c', "text": 'Дукесса Альба.'},
        ],
    },
    1045: {
        "question": 'При каком короле была восстановлена демократия в Испании после режима Франко?',
        "answer": 'При Хуане Карлосе I.',
        "options": [
            {"label": 'a', "text": 'С Карлосом III.'},
            {"label": 'b', "text": 'С Альфонсо XIII.'},
            {"label": 'c', "text": 'С Хуаном Карлосом I.'},
        ],
    },
    1046: {
        "question": 'В каком году была принята Конституция Испании?',
        "answer": 'В 1978 году.',
        "options": [
            {"label": 'a', "text": 'В 1957 году.'},
            {"label": 'b', "text": 'В 1978 году.'},
            {"label": 'c', "text": 'В 2001 году.'},
        ],
    },
    1047: {
        "question": 'Сколько автономных сообществ имеют свой флаг?',
        "answer": 'Все.',
        "options": [
            {"label": 'a', "text": 'Никакая.'},
            {"label": 'b', "text": 'Все.'},
            {"label": 'c', "text": 'Те, у кого есть коофициальный язык.'},
        ],
    },
    1048: {
        "question": 'Какой официальный орган рассматривает жалобы граждан на работу администрации?',
        "answer": 'Народный защитник.',
        "options": [
            {"label": 'a', "text": 'Офис по защите прав потребителей.'},
            {"label": 'b', "text": 'Национальная полиция.'},
            {"label": 'c', "text": 'Уполномоченный по правам человека.'},
        ],
    },
    1049: {
        "question": 'Сколько подписей минимум должны собрать граждане для внесения законопроекта?',
        "answer": '500 000.',
        "options": [
            {"label": 'a', "text": '250 000.'},
            {"label": 'b', "text": '100 000.'},
            {"label": 'c', "text": '500 000.'},
        ],
    },
    1050: {
        "question": 'К какой международной организации принадлежит Испания?',
        "answer": 'Международный валютный фонд (МВФ).',
        "options": [
            {"label": 'a', "text": 'Содружество Независимых Государств (СНГ).'},
            {"label": 'b', "text": 'Международный валютный фонд (МВФ).'},
            {"label": 'c', "text": 'Евразийский экономический союз (ЕАЭС).'},
        ],
    },
    1051: {
        "question": 'В организации администрации выделяют три уровня: центральный, региональный и…',
        "answer": 'местный.',
        "options": [
            {"label": 'a', "text": 'государственный'},
            {"label": 'b', "text": 'региональный'},
            {"label": 'c', "text": 'местный'},
        ],
    },
    1052: {
        "question": 'Законодательная власть принадлежит…',
        "answer": 'депутатам и сенаторам.',
        "options": [
            {"label": 'a', "text": 'к президенту и министрам.'},
            {"label": 'b', "text": 'судьям и магистратам.'},
            {"label": 'c', "text": 'к депутатам и сенаторам.'},
        ],
    },
    1053: {
        "question": 'Где живёт король?',
        "answer": 'Во дворце Сарсуэла.',
        "options": [
            {"label": 'a', "text": 'В Дворце Монеда.'},
            {"label": 'b', "text": 'В дворце Сарсуэла.'},
            {"label": 'c', "text": 'В Palacio de la Moncloa.'},
        ],
    },
    1054: {
        "question": 'Официальное название испанского парламента…',
        "answer": 'Генеральные кортесы.',
        "options": [
            {"label": 'a', "text": 'Генеральные кортесы.'},
            {"label": 'b', "text": 'Конгресс депутатов.'},
            {"label": 'c', "text": 'Сенат.'},
        ],
    },
    1055: {
        "question": 'Институт внешней торговли, Институт женщин и Главное управление дорожного движения…',
        "answer": 'подчиняются министерствам.',
        "options": [
            {"label": 'a', "text": 'это автономные организмы.'},
            {"label": 'b', "text": 'зависят от министерств.'},
            {"label": 'c', "text": 'это международные организации.'},
        ],
    },
    1056: {
        "question": 'Кто может царствовать в Испании?',
        "answer": 'Как мужчины, так и женщины.',
        "options": [
            {"label": 'a', "text": 'Только мужчины.'},
            {"label": 'b', "text": 'Только женщины.'},
            {"label": 'c', "text": 'Как мужчины, так и женщины.'},
        ],
    },
    1057: {
        "question": 'Счётная палата подчиняется…',
        "answer": 'Генеральным кортесам.',
        "options": [
            {"label": 'a', "text": 'Президентство правительства.'},
            {"label": 'b', "text": 'Генеральные кортесы.'},
            {"label": 'c', "text": 'Министерство финансов.'},
        ],
    },
    1058: {
        "question": 'Кто является третьим лицом государства после короля и председателя правительства?',
        "answer": 'Председатель Конгресса депутатов.',
        "options": [
            {"label": 'a', "text": 'Президент Сената.'},
            {"label": 'b', "text": 'Министр экономики.'},
            {"label": 'c', "text": 'Президент Конгресса депутатов.'},
        ],
    },
    1059: {
        "question": 'Какой соофициальный язык используется на Балеарских островах?',
        "answer": 'Каталанский.',
        "options": [
            {"label": 'a', "text": 'Президент правительства.'},
            {"label": 'b', "text": 'Король.'},
            {"label": 'c', "text": 'Директор Королевской академии испанского языка.'},
        ],
    },
    1060: {
        "question": 'Конституция защищает такие ценности, как свобода, равенство, политический плюрализм и…',
        "answer": 'справедливость.',
        "options": [
            {"label": 'a', "text": 'судебная система'},
            {"label": 'b', "text": 'солидарность'},
            {"label": 'c', "text": 'братство.'},
        ],
    },
    1061: {
        "question": 'Когда закон уже принят, что нужно для его применения?',
        "answer": 'Подзаконные акты для его развития.',
        "options": [
            {"label": 'a', "text": 'Ничего.'},
            {"label": 'b', "text": 'Нормы, которые ее развивают.'},
            {"label": 'c', "text": 'Подлежит рассмотрению парламентом.'},
        ],
    },
    1062: {
        "question": 'Сколько жителей в Испании?',
        "answer": '49 миллионов.',
        "options": [
            {"label": 'a', "text": '95 миллионов.'},
            {"label": 'b', "text": '49 миллионов.'},
            {"label": 'c', "text": '67 миллионов.'},
        ],
    },
    1063: {
        "question": 'Какой из этих органов является консультативным органом правительства Испании?',
        "answer": 'Государственный совет.',
        "options": [
            {"label": 'a', "text": 'Европейский парламент.'},
            {"label": 'b', "text": 'Государственный совет.'},
            {"label": 'c', "text": 'Конституционный суд.'},
        ],
    },
    1064: {
        "question": 'Кто руководит внутренней и внешней политикой Испании?',
        "answer": 'Правительство.',
        "options": [
            {"label": 'a', "text": 'Король.'},
            {"label": 'b', "text": 'Правительство.'},
            {"label": 'c', "text": 'Конгресс депутатов.'},
        ],
    },
    1065: {
        "question": 'Народный защитник подчиняется…',
        "answer": 'Генеральным кортесам.',
        "options": [
            {"label": 'a', "text": 'Совет Министров.'},
            {"label": 'b', "text": 'Счетная палата.'},
            {"label": 'c', "text": 'Генеральные кортесы.'},
        ],
    },
    1066: {
        "question": 'Институт Этчепаре занимается распространением…',
        "answer": 'баскского языка и баскской культуры.',
        "options": [
            {"label": 'a', "text": 'баскский язык и баскская культура.'},
            {"label": 'b', "text": 'бабле и кантабрийская культура.'},
            {"label": 'c', "text": 'галего и галисийская культура.'},
        ],
    },
    1067: {
        "question": 'Какой из этих городов входит в десятку самых населённых в Испании?',
        "answer": 'Малага.',
        "options": [
            {"label": 'a', "text": 'Кадис.'},
            {"label": 'b', "text": 'Малага.'},
            {"label": 'c', "text": 'Альбасете.'},
        ],
    },
    1068: {
        "question": 'Кто может совершать административные процедуры онлайн?',
        "answer": 'Любой гражданин.',
        "options": [
            {"label": 'a', "text": 'Судьи и магистраты.'},
            {"label": 'b', "text": 'Любой гражданин.'},
            {"label": 'c', "text": 'Адвокаты, состоящие в коллегии.'},
        ],
    },
    1069: {
        "question": 'Как зовут короля Испании?',
        "answer": 'Филипп VI.',
        "options": [
            {"label": 'a', "text": 'Хуан Карлос I.'},
            {"label": 'b', "text": 'Фелипе VI.'},
            {"label": 'c', "text": 'Альфонсо XIII.'},
        ],
    },
    1070: {
        "question": 'Как называется орган управления судьями и магистратами?',
        "answer": 'Генеральный совет судебной власти.',
        "options": [
            {"label": 'a', "text": 'Верховный суд.'},
            {"label": 'b', "text": 'Совет генерального судебного управления.'},
            {"label": 'c', "text": 'Государственный совет.'},
        ],
    },
    1071: {
        "question": 'Кто утверждает государственный бюджет?',
        "answer": 'Генеральные кортесы.',
        "options": [
            {"label": 'a', "text": 'Генеральные кортесы.'},
            {"label": 'b', "text": 'Счетная палата.'},
            {"label": 'c', "text": 'Правительство Испании.'},
        ],
    },
    1072: {
        "question": 'Конституция Испании — это…',
        "answer": 'основной закон.',
        "options": [
            {"label": 'a', "text": 'основной закон'},
            {"label": 'b', "text": 'часть другого закона.'},
            {"label": 'c', "text": 'вторичный закон.'},
        ],
    },
    1073: {
        "question": 'Генеральные кортесы состоят из Сената и…',
        "answer": 'Конгресса депутатов.',
        "options": [
            {"label": 'a', "text": 'Конгресс депутатов.'},
            {"label": 'b', "text": 'Верховный суд.'},
            {"label": 'c', "text": 'Государственный совет.'},
        ],
    },
    1074: {
        "question": 'Кто разрабатывает законы?',
        "answer": 'Законодательная власть.',
        "options": [
            {"label": 'a', "text": 'Исполнительная власть.'},
            {"label": 'b', "text": 'Законодательная власть.'},
            {"label": 'c', "text": 'Судебная власть.'},
        ],
    },
    1075: {
        "question": 'Защита территориальной целостности Испании возложена на…',
        "answer": 'Вооружённые силы.',
        "options": [
            {"label": 'a', "text": 'Национальная полиция и Гражданская гвардия.'},
            {"label": 'b', "text": 'Вооруженные силы.'},
            {"label": 'c', "text": 'Национальная полиция и автономные полиции.'},
        ],
    },
    1076: {
        "question": 'С 1989 года испанская армия участвует в миротворческих миссиях…',
        "answer": 'Организации Объединённых Наций (ООН).',
        "options": [
            {"label": 'a', "text": 'Организация ибероамериканских государств (ОИГ).'},
            {"label": 'b', "text": 'Западное Европейское Союз (ЗЕС).'},
            {"label": 'c', "text": 'Организация Объединённых Наций (ООН).'},
        ],
    },
    1077: {
        "question": 'Кто охраняет порты, аэропорты, границы и побережье?',
        "answer": 'Гражданская гвардия.',
        "options": [
            {"label": 'a', "text": 'Гражданская гвардия.'},
            {"label": 'b', "text": 'Местная полиция.'},
            {"label": 'c', "text": 'Национальная полиция.'},
        ],
    },
    1078: {
        "question": 'Кто осуществляет паспортный контроль на границах Испании?',
        "answer": 'Национальная полиция.',
        "options": [
            {"label": 'a', "text": 'Гражданская гвардия.'},
            {"label": 'b', "text": 'Местная полиция.'},
            {"label": 'c', "text": 'Национальная полиция.'},
        ],
    },
    1079: {
        "question": 'Кто из этих политиков был председателем правительства Испании?',
        "answer": 'Хосе Мария Аснар.',
        "options": [
            {"label": 'a', "text": 'Мануэль Фрага.'},
            {"label": 'b', "text": 'Хосе Мария Аснар.'},
            {"label": 'c', "text": 'Йоланда Диас.'},
        ],
    },
    1080: {
        "question": 'Как называется автономная полиция Каталонии?',
        "answer": "Моссос д'Эсквадра.",
        "options": [
            {"label": 'a', "text": 'Гражданская гвардия.'},
            {"label": 'b', "text": 'Эрцайца.'},
            {"label": 'c', "text": "Моссос д'Эсквадра."},
        ],
    },
    1081: {
        "question": 'Как называется автономная полиция Страны Басков?',
        "answer": 'Эрцайнца.',
        "options": [
            {"label": 'a', "text": 'Эрцайцунца.'},
            {"label": 'b', "text": 'Гражданская гвардия.'},
            {"label": 'c', "text": "Моссос д'Эсквадра."},
        ],
    },
    1082: {
        "question": 'С какого года Филипп VI является королём?',
        "answer": 'С 2014 года.',
        "options": [
            {"label": 'a', "text": 'С 1975 года.'},
            {"label": 'b', "text": 'С 2014 года.'},
            {"label": 'c', "text": 'С 2020 года.'},
        ],
    },
    1083: {
        "question": 'Кто регулирует дорожное движение в населённых пунктах?',
        "answer": 'Местная полиция.',
        "options": [
            {"label": 'a', "text": 'Гражданская гвардия.'},
            {"label": 'b', "text": 'Гражданская защита.'},
            {"label": 'c', "text": 'Местная полиция.'},
        ],
    },
    1084: {
        "question": 'Кто может подать жалобу Народному защитнику?',
        "answer": 'Все граждане, испанцы и иностранцы.',
        "options": [
            {"label": 'a', "text": 'Только законно проживающие граждане.'},
            {"label": 'b', "text": 'Только испанцы старше 18 лет.'},
            {"label": 'c', "text": 'Все граждане, испанцы или иностранцы.'},
        ],
    },
    1085: {
        "question": 'В Испании голосование на выборах — это…',
        "answer": 'право.',
        "options": [
            {"label": 'a', "text": 'право'},
            {"label": 'b', "text": 'обязанность'},
            {"label": 'c', "text": 'обязанность.'},
        ],
    },
    1086: {
        "question": 'Кто контролирует дорожное движение на автомагистралях?',
        "answer": 'Гражданская гвардия.',
        "options": [
            {"label": 'a', "text": 'Гражданская гвардия.'},
            {"label": 'b', "text": 'Национальная полиция.'},
            {"label": 'c', "text": 'Сухопутные войска.'},
        ],
    },
    1087: {
        "question": 'Какой орган занимается сбором налогов?',
        "answer": 'Налоговое агентство.',
        "options": [
            {"label": 'a', "text": 'Счетная палата.'},
            {"label": 'b', "text": 'Налоговая служба.'},
            {"label": 'c', "text": 'Экономический и социальный совет.'},
        ],
    },
    1088: {
        "question": 'Где публикуются национальные законы?',
        "answer": 'В Официальном государственном бюллетене (BOE).',
        "options": [
            {"label": 'a', "text": 'В бюллетене Национального института статистики (INE).'},
            {"label": 'b', "text": 'На Портале Электронного Управления (PAe).'},
            {"label": 'c', "text": 'В Официальном государственном бюллетене (BOE).'},
        ],
    },
    1089: {
        "question": 'Как называются органы управления, существующие только на Канарских островах?',
        "answer": 'Кабильдо.',
        "options": [
            {"label": 'a', "text": 'Кабильдос.'},
            {"label": 'b', "text": 'Островные советы.'},
            {"label": 'c', "text": 'Депутаты.'},
        ],
    },
    1090: {
        "question": 'Какую административную процедуру можно выполнить на электронном портале?',
        "answer": 'Уплатить налоги.',
        "options": [
            {"label": 'a', "text": 'Оформить DNI.'},
            {"label": 'b', "text": 'Обновить паспорт.'},
            {"label": 'c', "text": 'Платить налоги.'},
        ],
    },
    1091: {
        "question": 'Какой номер телефона информационной службы государственной администрации?',
        "answer": '060.',
        "options": [
            {"label": 'a', "text": '010.'},
            {"label": 'b', "text": '060.'},
            {"label": 'c', "text": '091.'},
        ],
    },
    1092: {
        "question": 'Испания организована в…',
        "answer": 'автономные сообщества.',
        "options": [
            {"label": 'a', "text": 'кантоны'},
            {"label": 'b', "text": 'автономные сообщества'},
            {"label": 'c', "text": 'федеральные штаты'},
        ],
    },
    1093: {
        "question": 'Сколько политических партий в Испании?',
        "answer": 'Много.',
        "options": [
            {"label": 'a', "text": 'Никто.'},
            {"label": 'b', "text": 'Один.'},
            {"label": 'c', "text": 'Много.'},
        ],
    },
    1094: {
        "question": 'Где проходит инвеститура председателя правительства?',
        "answer": 'В Конгрессе депутатов.',
        "options": [
            {"label": 'a', "text": 'В Дворце Монклоа.'},
            {"label": 'b', "text": 'В Конгрессе депутатов.'},
            {"label": 'c', "text": 'В Сенате.'},
        ],
    },
    1095: {
        "question": 'Кто является верховным главнокомандующим Вооружёнными силами?',
        "answer": 'Король.',
        "options": [
            {"label": 'a', "text": 'Король.'},
            {"label": 'b', "text": 'Президент правительства.'},
            {"label": 'c', "text": 'Министр обороны.'},
        ],
    },
    1096: {
        "question": 'Кто является представителем государства в автономном сообществе?',
        "answer": 'Правительственный делегат.',
        "options": [
            {"label": 'a', "text": 'Президент автономного сообщества.'},
            {"label": 'b', "text": 'Делегат правительства.'},
            {"label": 'c', "text": 'Президент автономной ассамблеи.'},
        ],
    },
    1097: {
        "question": 'Сколько провинций в Испании?',
        "answer": '50.',
        "options": [
            {"label": 'a', "text": '45.'},
            {"label": 'b', "text": '50.'},
            {"label": 'c', "text": '55.'},
        ],
    },
    1098: {
        "question": 'Преподавание соофициальных языков относится к компетенции…',
        "answer": 'автономного сообщества.',
        "options": [
            {"label": 'a', "text": 'государства.'},
            {"label": 'b', "text": 'автономного сообщества.'},
            {"label": 'c', "text": 'из провинции.'},
        ],
    },
    1099: {
        "question": 'Исполнительная власть принадлежит…',
        "answer": 'правительству государства.',
        "options": [
            {"label": 'a', "text": 'Государственному правительству.'},
            {"label": 'b', "text": 'в Конгресс и в Сенат.'},
            {"label": 'c', "text": 'судьям и магистратам.'},
        ],
    },
    1100: {
        "question": 'Сколько палат в испанском парламенте?',
        "answer": 'Две.',
        "options": [
            {"label": 'a', "text": 'Одна.'},
            {"label": 'b', "text": 'Два.'},
            {"label": 'c', "text": 'Три.'},
        ],
    },
    1101: {
        "question": 'Водоснабжение и уличное освещение городов относятся к компетенции…',
        "answer": 'муниципалитета.',
        "options": [
            {"label": 'a', "text": 'муниципалитет'},
            {"label": 'b', "text": 'автономное правительство'},
            {"label": 'c', "text": 'Министерство общественных работ и градостроительства.'},
        ],
    },
    1102: {
        "question": 'В вопросах гражданства, иммиграции, эмиграции и иностранцев компетентен только…',
        "answer": 'государство.',
        "options": [
            {"label": 'a', "text": 'государство.'},
            {"label": 'b', "text": 'автономные сообщества'},
            {"label": 'c', "text": 'муниципалитеты.'},
        ],
    },
    1103: {
        "question": 'Сколько женщин были председателями правительства Испании?',
        "answer": 'Ни одной.',
        "options": [
            {"label": 'a', "text": 'Никакая.'},
            {"label": 'b', "text": 'Одна.'},
            {"label": 'c', "text": 'Два.'},
        ],
    },
    1104: {
        "question": 'Международные отношения относятся к компетенции…',
        "answer": 'государства.',
        "options": [
            {"label": 'a', "text": 'государство.'},
            {"label": 'b', "text": 'автономные сообщества'},
            {"label": 'c', "text": 'муниципалитеты.'},
        ],
    },
    1105: {
        "question": 'Муниципалитет состоит из мэра и…',
        "answer": 'членов муниципального совета.',
        "options": [
            {"label": 'a', "text": 'советники.'},
            {"label": 'b', "text": 'депутаты.'},
            {"label": 'c', "text": 'сенаторы.'},
        ],
    },
    1106: {
        "question": 'Кто формирует правительство автономных сообществ?',
        "answer": 'Президент и советники.',
        "options": [
            {"label": 'a', "text": 'Президент и министры.'},
            {"label": 'b', "text": 'Мэр и советники.'},
            {"label": 'c', "text": 'Президент и советники.'},
        ],
    },
    1107: {
        "question": 'Какой орган управления в муниципалитетах?',
        "answer": 'Муниципалитет (Ayuntamiento).',
        "options": [
            {"label": 'a', "text": 'Городская ратуша.'},
            {"label": 'b', "text": 'Депутация.'},
            {"label": 'c', "text": 'Кабильдо.'},
        ],
    },
    1108: {
        "question": 'Как называются органы управления испанских провинций?',
        "answer": 'Провинциальные советы (Diputaciones).',
        "options": [
            {"label": 'a', "text": 'Кабильдос.'},
            {"label": 'b', "text": 'Островные советы.'},
            {"label": 'c', "text": 'Депутации.'},
        ],
    },
    1109: {
        "question": 'Какой высший орган исполнительной власти?',
        "answer": 'Правительство.',
        "options": [
            {"label": 'a', "text": 'Правительство.'},
            {"label": 'b', "text": 'Вооруженные Силы.'},
            {"label": 'c', "text": 'Генеральные кортесы.'},
        ],
    },
    1110: {
        "question": 'Испанский язык также называется…',
        "answer": 'кастильским.',
        "options": [
            {"label": 'a', "text": 'арагонский'},
            {"label": 'b', "text": 'кастильский'},
            {"label": 'c', "text": 'леонский'},
        ],
    },
    1111: {
        "question": 'Кого выбирают на выборах в Европейский парламент?',
        "answer": 'Евродепутатов.',
        "options": [
            {"label": 'a', "text": 'Европейским министрам.'},
            {"label": 'b', "text": 'К генеральным директорам.'},
            {"label": 'c', "text": 'К евродепутатам.'},
        ],
    },
    1112: {
        "question": 'Испанцы могут голосовать с…',
        "answer": '18 лет.',
        "options": [
            {"label": 'a', "text": '16 лет.'},
            {"label": 'b', "text": '18 лет.'},
            {"label": 'c', "text": '21 лет.'},
        ],
    },
    1113: {
        "question": 'Некоторые иностранные граждане могут голосовать на…выборах.',
        "answer": 'муниципальных.',
        "options": [
            {"label": 'a', "text": 'муниципальные'},
            {"label": 'b', "text": 'автономные'},
            {"label": 'c', "text": 'генералы.'},
        ],
    },
    1114: {
        "question": 'Кто контролирует финансовое управление государства?',
        "answer": 'Счётная палата.',
        "options": [
            {"label": 'a', "text": 'Испанский банк.'},
            {"label": 'b', "text": 'Налоговая служба.'},
            {"label": 'c', "text": 'Счетная палата.'},
        ],
    },
    1115: {
        "question": 'Кого выбирают на всеобщих выборах?',
        "answer": 'Сенаторов и депутатов.',
        "options": [
            {"label": 'a', "text": 'К сенаторам и депутатам.'},
            {"label": 'b', "text": 'К евродепутатам.'},
            {"label": 'c', "text": 'К советникам.'},
        ],
    },
    1116: {
        "question": 'Сколько членов в Конгрессе депутатов?',
        "answer": '350.',
        "options": [
            {"label": 'a', "text": '300.'},
            {"label": 'b', "text": '350.'},
            {"label": 'c', "text": '400.'},
        ],
    },
    1117: {
        "question": 'Муниципалитеты и провинции входят в состав…администрации.',
        "answer": 'местной.',
        "options": [
            {"label": 'a', "text": 'автономный'},
            {"label": 'b', "text": 'местный'},
            {"label": 'c', "text": 'центральный'},
        ],
    },
    1118: {
        "question": 'Самое населённое автономное сообщество Испании — это…',
        "answer": 'Андалусия.',
        "options": [
            {"label": 'a', "text": 'Андалусия.'},
            {"label": 'b', "text": 'Каталония.'},
            {"label": 'c', "text": 'Кастилия и Леон.'},
        ],
    },
    1119: {
        "question": 'Как называется организация, защищающая интересы трудящихся?',
        "answer": 'Профсоюз.',
        "options": [
            {"label": 'a', "text": 'Ассоциация.'},
            {"label": 'b', "text": 'Партия.'},
            {"label": 'c', "text": 'Союз.'},
        ],
    },
    1120: {
        "question": 'Кто избирает председателя правительства?',
        "answer": 'Конгресс депутатов.',
        "options": [
            {"label": 'a', "text": 'Конгресс депутатов.'},
            {"label": 'b', "text": 'Король.'},
            {"label": 'c', "text": 'Верховный суд.'},
        ],
    },
    2001: {
        "question": 'В Испании Конституция обязывает всех граждан исповедовать религию.',
        "answer": 'Ложь.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2002: {
        "question": 'Испанцы, получившие гражданство по проживанию, должны ждать три года, чтобы голосовать.',
        "answer": 'Ложь.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2003: {
        "question": 'В Испании Конституция запрещает пытки и смертную казнь.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2004: {
        "question": 'Деятельность политических партий должна быть демократической.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2005: {
        "question": 'Можно заставить человека раскрыть свои политические или религиозные взгляды.',
        "answer": 'Ложь.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2006: {
        "question": 'Можно ограничить право человека свободно въезжать и выезжать из Испании по идеологическим причинам.',
        "answer": 'Ложь.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2007: {
        "question": 'Начальное образование (от 6 до 12 лет) бесплатное и обязательное.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2008: {
        "question": 'Конституция гарантирует право испанцев на достойное жильё.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2009: {
        "question": 'В Испании полиция может войти в любой дом без судебного решения в любое время.',
        "answer": 'Ложь.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2010: {
        "question": 'Тайна переписки испанцев гарантируется, за исключением судебного решения.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2011: {
        "question": 'Конституция признаёт право граждан свободно объединяться.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2012: {
        "question": 'Преподаватели могут свободно преподавать в рамках Конституции.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2013: {
        "question": 'Конституция признаёт только основные права испанцев.',
        "answer": 'Ложь.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2014: {
        "question": 'Граждане должны сотрудничать с судьями, если их об этом попросят.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2015: {
        "question": 'Закон ограничивает доступ третьих лиц к персональным данным.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2016: {
        "question": 'Свобода прессы ограничена уважением к чести людей.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2017: {
        "question": 'В Испании причины раздельного проживания и развода регулируются законом.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2018: {
        "question": 'Бесплатная медицинская помощь предоставляется только лицам старше 65 лет.',
        "answer": 'Ложь.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2019: {
        "question": 'В Испании мужчины и женщины имеют равные права.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Правда.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2020: {
        "question": 'Обязательное образование состоит из двух этапов: начальное и обязательное среднее.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2021: {
        "question": 'В Испании есть официальная религия.',
        "answer": 'Ложь.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2022: {
        "question": 'Государственная медицинская помощь бесплатна.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Правда.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2023: {
        "question": 'Базовое образование в Испании предназначено только для иностранцев.',
        "answer": 'Ложь.',
        "options": [
            {"label": 'a', "text": 'Правда.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2024: {
        "question": 'В Испании признано право на объединение.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2025: {
        "question": 'Профсоюзы могут участвовать в переговорах с работодателями и правительством.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Верно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2026: {
        "question": 'Работники имеют право на забастовку.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2027: {
        "question": 'Идеологическая свобода гарантируется только на части национальной территории.',
        "answer": 'Ложь.',
        "options": [
            {"label": 'a', "text": 'Правда.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2028: {
        "question": 'Все граждане имеют доступ к системе социального обеспечения, кроме безработных.',
        "answer": 'Ложь.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2029: {
        "question": 'Все имеют право на благоприятную окружающую среду и обязаны её сохранять.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2030: {
        "question": 'В Испании государственные органы должны охранять здоровье и содействовать спорту.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Правда.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2031: {
        "question": 'Базовое образование в Испании обязательное и бесплатное.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2032: {
        "question": 'Закон запрещает дискриминацию по любым личным или социальным обстоятельствам.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2033: {
        "question": 'В Испании граждане могут свободно перемещаться по всей национальной территории.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложно.'},
        ],
    },
    2034: {
        "question": 'Судьи отправляют правосудие в Испании по указаниям правительства.',
        "answer": 'Ложь.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2035: {
        "question": 'Испанцы должны помогать в случаях катастроф или общественных бедствий.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    2036: {
        "question": 'В Испании граждане могут выбирать, в каком городе жить.',
        "answer": 'Правда.',
        "options": [
            {"label": 'a', "text": 'Истинно.'},
            {"label": 'b', "text": 'Ложь.'},
        ],
    },
    3001: {
        "question": 'Где находятся Касерес и Бадахос?',
        "answer": 'В Эстремадуре.',
        "options": [
            {"label": 'a', "text": 'В княжестве Астурия.'},
            {"label": 'b', "text": 'В Андалусии.'},
            {"label": 'c', "text": 'В Эстремадуре.'},
        ],
    },
    3002: {
        "question": 'Какая столица Валенсийского сообщества?',
        "answer": 'Валенсия.',
        "options": [
            {"label": 'a', "text": 'Аликанте.'},
            {"label": 'b', "text": 'Кастельон.'},
            {"label": 'c', "text": 'Валенсия.'},
        ],
    },
    3003: {
        "question": 'Где находятся Балеарские острова?',
        "answer": 'В Средиземном море.',
        "options": [
            {"label": 'a', "text": 'На Кантабрийском море.'},
            {"label": 'b', "text": 'В Средиземном море.'},
            {"label": 'c', "text": 'В Атлантическом океане.'},
        ],
    },
    3004: {
        "question": 'Как называется обширная равнина в центре Пиренейского полуострова?',
        "answer": 'Месета.',
        "options": [
            {"label": 'a', "text": 'Марш.'},
            {"label": 'b', "text": 'Кордильера.'},
            {"label": 'c', "text": 'Месета.'},
        ],
    },
    3005: {
        "question": 'Национальный парк Ордеса находится в...',
        "answer": 'Арагоне.',
        "options": [
            {"label": 'a', "text": 'Арагон.'},
            {"label": 'b', "text": 'Наварра.'},
            {"label": 'c', "text": 'Кастилия-Ла-Манча.'},
        ],
    },
    3006: {
        "question": 'В каком автономном сообществе находятся Гвадалахара и Куэнка?',
        "answer": 'В Кастилии-Ла-Манче.',
        "options": [
            {"label": 'a', "text": 'В Кастилии и Леоне.'},
            {"label": 'b', "text": 'В Кастилье-Ла-Манче.'},
            {"label": 'c', "text": 'В Кантабрии.'},
        ],
    },
    3007: {
        "question": 'Какое автономное сообщество имеет столицу Сантьяго-де-Компостела?',
        "answer": 'Галисия.',
        "options": [
            {"label": 'a', "text": 'Галисия.'},
            {"label": 'b', "text": 'Астурия.'},
            {"label": 'c', "text": 'Кантабрия.'},
        ],
    },
    3008: {
        "question": 'Где находится Альмерия?',
        "answer": 'В Андалусии.',
        "options": [
            {"label": 'a', "text": 'В Андалусии.'},
            {"label": 'b', "text": 'На Канарах.'},
            {"label": 'c', "text": 'В Араагоне.'},
        ],
    },
    3009: {
        "question": 'Столица автономного сообщества Галисия — это…',
        "answer": 'Сантьяго-де-Компостела.',
        "options": [
            {"label": 'a', "text": 'А Корунья.'},
            {"label": 'b', "text": 'Виго.'},
            {"label": 'c', "text": 'Сантьяго-де-Компостела.'},
        ],
    },
    3010: {
        "question": 'Какая из этих рек впадает в Средиземное море?',
        "answer": 'Хукар.',
        "options": [
            {"label": 'a', "text": 'Эль Тахо.'},
            {"label": 'b', "text": 'Эль-Хукар.'},
            {"label": 'c', "text": 'Дуэро.'},
        ],
    },
    3011: {
        "question": 'Где находится гора Ането?',
        "answer": 'В Пиренеях.',
        "options": [
            {"label": 'a', "text": 'В Пиренеях.'},
            {"label": 'b', "text": 'В Центральной системе.'},
            {"label": 'c', "text": 'В Сьерра-Неваде.'},
        ],
    },
    3012: {
        "question": 'Город Витория является административным центром…',
        "answer": 'Страны Басков.',
        "options": [
            {"label": 'a', "text": 'Наварра.'},
            {"label": 'b', "text": 'Страна Басков.'},
            {"label": 'c', "text": 'Ла Риоха.'},
        ],
    },
    3013: {
        "question": 'Испания делится на…',
        "answer": 'автономные сообщества и города.',
        "options": [
            {"label": 'a', "text": 'департаменты и регионы.'},
            {"label": 'b', "text": 'автономные сообщества и города'},
            {"label": 'c', "text": 'автономные регионы и районы.'},
        ],
    },
    3014: {
        "question": 'Национальный парк Айгуэстортес находится в...',
        "answer": 'Каталонии.',
        "options": [
            {"label": 'a', "text": 'Каталония.'},
            {"label": 'b', "text": 'Арагон'},
            {"label": 'c', "text": 'Кастилия и Леон.'},
        ],
    },
    3015: {
        "question": 'На севере Африки находятся Сеута и…',
        "answer": 'Мелилья.',
        "options": [
            {"label": 'a', "text": 'Альмерия.'},
            {"label": 'b', "text": 'Мелилья.'},
            {"label": 'c', "text": 'Кадис.'},
        ],
    },
    3016: {
        "question": 'В какой части Испании климат характеризуется холодной зимой и очень жарким летом?',
        "answer": 'Мадрид.',
        "options": [
            {"label": 'a', "text": 'Канары.'},
            {"label": 'b', "text": 'Валенсийское сообщество.'},
            {"label": 'c', "text": 'Мадрид.'},
        ],
    },
    3017: {
        "question": 'Какая из этих рек впадает в Атлантический океан?',
        "answer": 'Гвадалквивир.',
        "options": [
            {"label": 'a', "text": 'Гвадалквивир.'},
            {"label": 'b', "text": 'Эль Мансанарес.'},
            {"label": 'c', "text": 'Эль-Хукар.'},
        ],
    },
    3018: {
        "question": 'Какая из этих провинций входит в состав Кастилии и Леона?',
        "answer": 'Бургос.',
        "options": [
            {"label": 'a', "text": 'Бургос.'},
            {"label": 'b', "text": 'Уэска.'},
            {"label": 'c', "text": 'Гвадалахара.'},
        ],
    },
    3019: {
        "question": 'В каком автономном сообществе находится город Уэска?',
        "answer": 'Арагон.',
        "options": [
            {"label": 'a', "text": 'Кастилия-Ла-Манча.'},
            {"label": 'b', "text": 'Арагон.'},
            {"label": 'c', "text": 'Эстремадура.'},
        ],
    },
    3020: {
        "question": 'На Канарских островах…климат.',
        "answer": 'субтропический.',
        "options": [
            {"label": 'a', "text": 'Средиземное море.'},
            {"label": 'b', "text": 'океанический'},
            {"label": 'c', "text": 'субтропический'},
        ],
    },
    3021: {
        "question": 'Главная река, впадающая в Средиземное море, — это…',
        "answer": 'Эбро.',
        "options": [
            {"label": 'a', "text": 'Эбро.'},
            {"label": 'b', "text": 'Дуэро.'},
            {"label": 'c', "text": 'Тахо.'},
        ],
    },
    3022: {
        "question": 'Испания входит в число наиболее…стран Европы.',
        "answer": 'гористых.',
        "options": [
            {"label": 'a', "text": 'дождливые'},
            {"label": 'b', "text": 'гористые'},
            {"label": 'c', "text": 'холодные.'},
        ],
    },
    3023: {
        "question": 'В какой провинции находится национальный парк Монфрагуэ?',
        "answer": 'В Касересе.',
        "options": [
            {"label": 'a', "text": 'В Касересе.'},
            {"label": 'b', "text": 'В Мурсии.'},
            {"label": 'c', "text": 'В Сьюдад-Реале.'},
        ],
    },
    3024: {
        "question": 'Какая столица автономного сообщества Эстремадура?',
        "answer": 'Мерида.',
        "options": [
            {"label": 'a', "text": 'Касерес.'},
            {"label": 'b', "text": 'Бадахос.'},
            {"label": 'c', "text": 'Мерида.'},
        ],
    },
    4001: {
        "question": 'Главные персонажи романа «Дон Кихот» — Дон Кихот и…',
        "answer": 'Санчо Панса.',
        "options": [
            {"label": 'a', "text": 'Дон Жуан.'},
            {"label": 'b', "text": 'Санчо Панса.'},
            {"label": 'c', "text": 'Донья Инес.'},
        ],
    },
    4002: {
        "question": 'Какая испанская учёная известна своими исследованиями?',
        "answer": 'Маргарита Салас.',
        "options": [
            {"label": 'a', "text": 'Алмудена Гранде.'},
            {"label": 'b', "text": 'Монтсеррат Кабалье.'},
            {"label": 'c', "text": 'Маргарита Салас.'},
        ],
    },
    4003: {
        "question": 'Кто написал «Дом Бернарды Альбы»?',
        "answer": 'Федерико Гарсиа Лорка.',
        "options": [
            {"label": 'a', "text": 'Федерико Гарсия Лорка.'},
            {"label": 'b', "text": 'Мигель де Сервантес.'},
            {"label": 'c', "text": 'Антонио Мачадо.'},
        ],
    },
    4004: {
        "question": 'Кто написал «Ничто» — роман о послевоенной Испании?',
        "answer": 'Кармен Лафорет.',
        "options": [
            {"label": 'a', "text": 'Кармен Лафорет.'},
            {"label": 'b', "text": 'Ана Мария Матуте.'},
            {"label": 'c', "text": 'Мария Дуэñas.'},
        ],
    },
    4005: {
        "question": 'Какой музыкант сочинил «Любовь-колдунью»?',
        "answer": 'Мануэль де Фалья.',
        "options": [
            {"label": 'a', "text": 'Мануэль де Фалья.'},
            {"label": 'b', "text": 'Исаак Альбенис.'},
            {"label": 'c', "text": 'Хоакин Родриго.'},
        ],
    },
    4006: {
        "question": 'Что характерно для ночи Святого Иоанна?',
        "answer": 'Зажигать костры.',
        "options": [
            {"label": 'a', "text": 'Есть виноград.'},
            {"label": 'b', "text": 'Разжигать костры.'},
            {"label": 'c', "text": 'Дарить книги.'},
        ],
    },
    4007: {
        "question": 'Какой инструмент наиболее характерен для музыки фламенко?',
        "answer": 'Гитара.',
        "options": [
            {"label": 'a', "text": 'Гайта.'},
            {"label": 'b', "text": 'Гитара.'},
            {"label": 'c', "text": 'Пиано.'},
        ],
    },
    4008: {
        "question": 'Исабель Коишет — это…',
        "answer": 'кинорежиссёр.',
        "options": [
            {"label": 'a', "text": 'поп-певец'},
            {"label": 'b', "text": 'классическая балерина.'},
            {"label": 'c', "text": 'кинорежиссёр'},
        ],
    },
    4009: {
        "question": 'Одна из самых известных испанских певиц сегодня — это...',
        "answer": 'Росалия.',
        "options": [
            {"label": 'a', "text": 'Росалия.'},
            {"label": 'b', "text": 'Марисоль.'},
            {"label": 'c', "text": 'Лола Флорес.'},
        ],
    },
    4010: {
        "question": 'В каком городе Испании есть мечеть, являющаяся объектом Всемирного наследия?',
        "answer": 'Кордова.',
        "options": [
            {"label": 'a', "text": 'Сантьяго-де-Компостела.'},
            {"label": 'b', "text": 'Мадрид.'},
            {"label": 'c', "text": 'Кордоба.'},
        ],
    },
    4011: {
        "question": 'В каком городе Испании находится Альгамбра — объект Всемирного наследия?',
        "answer": 'В Гранаде.',
        "options": [
            {"label": 'a', "text": 'В Севилье.'},
            {"label": 'b', "text": 'В Кордове.'},
            {"label": 'c', "text": 'В Гранаде.'},
        ],
    },
    4012: {
        "question": 'Как зовут испанского режиссёра, которая выделялась критическим взглядом и модернизировала национальное кино?',
        "answer": 'Пилар Миро.',
        "options": [
            {"label": 'a', "text": 'Пилар Миро.'},
            {"label": 'b', "text": 'Сара Барас.'},
            {"label": 'c', "text": 'Пенелопа Крус.'},
        ],
    },
    4013: {
        "question": 'Какой успешный роман написала Ирене Вальехо?',
        "answer": '«Бесконечность в тростинке».',
        "options": [
            {"label": 'a', "text": 'Бесконечность в тростнике.'},
            {"label": 'b', "text": 'Время между швами.'},
            {"label": 'c', "text": 'Дорога.'},
        ],
    },
    4014: {
        "question": 'Как называется крупнейшее государственное научно-исследовательское учреждение Испании?',
        "answer": 'Высший совет научных исследований (CSIC).',
        "options": [
            {"label": 'a', "text": 'Королевская академия испанского языка (RAE).'},
            {"label": 'b', "text": 'Высший совет научных исследований (CSIC).'},
            {"label": 'c', "text": 'Общество авторов (SGAE).'},
        ],
    },
    4015: {
        "question": 'Пако де Лусия был известным…',
        "answer": 'гитаристом.',
        "options": [
            {"label": 'a', "text": 'учёный'},
            {"label": 'b', "text": 'гитарист'},
            {"label": 'c', "text": 'художник'},
        ],
    },
    4016: {
        "question": 'Что мы празднуем 24 декабря?',
        "answer": 'Сочельник.',
        "options": [
            {"label": 'a', "text": 'Карнаваль.'},
            {"label": 'b', "text": 'Ночь добра.'},
            {"label": 'c', "text": 'Сан-Хуан.'},
        ],
    },
    4017: {
        "question": 'Хуан Мари Арсак — известный...',
        "answer": 'повар.',
        "options": [
            {"label": 'a', "text": 'писатель'},
            {"label": 'b', "text": 'музыкант'},
            {"label": 'c', "text": 'повар'},
        ],
    },
    4018: {
        "question": 'Кем была Клара Кампоамор?',
        "answer": 'Защитницей прав женщин.',
        "options": [
            {"label": 'a', "text": 'Защитница прав женщин.'},
            {"label": 'b', "text": 'Лирическая певица.'},
            {"label": 'c', "text": 'Режиссер.'},
        ],
    },
    4019: {
        "question": 'Какие традиционные песни поют на Рождество?',
        "answer": 'Вильянсикос (рождественские песни).',
        "options": [
            {"label": 'a', "text": 'Фламенко.'},
            {"label": 'b', "text": 'Рождественские песни.'},
            {"label": 'c', "text": 'Хоты.'},
        ],
    },
    4020: {
        "question": 'Лига и Кубок короля — это соревнования по…',
        "answer": 'футболу.',
        "options": [
            {"label": 'a', "text": 'плавание'},
            {"label": 'b', "text": 'атлетика'},
            {"label": 'c', "text": 'футбол'},
        ],
    },
    4021: {
        "question": 'Кто получил Нобелевскую премию по литературе?',
        "answer": 'Висенте Алейксандре.',
        "options": [
            {"label": 'a', "text": 'Мария Замбрано.'},
            {"label": 'b', "text": 'Пабло Пикассо.'},
            {"label": 'c', "text": 'Висенте Алехандре.'},
        ],
    },
    4022: {
        "question": 'Какой праздник отмечается в Памплоне 7 июля?',
        "answer": 'Сан-Фермин.',
        "options": [
            {"label": 'a', "text": 'Санфермины.'},
            {"label": 'b', "text": 'Фальяс.'},
            {"label": 'c', "text": 'Апрельская ярмарка.'},
        ],
    },
    4023: {
        "question": 'Тереса Пералес и Даниэль Молина — это...',
        "answer": 'паралимпийские чемпионы.',
        "options": [
            {"label": 'a', "text": 'паралимпийские чемпионы.'},
            {"label": 'b', "text": 'известные музыканты'},
            {"label": 'c', "text": 'кинематографисты'},
        ],
    },
    4024: {
        "question": 'Что едят испанцы в ночь на 31 декабря, отмечая Новый год?',
        "answer": 'Виноград.',
        "options": [
            {"label": 'a', "text": 'Чечевица.'},
            {"label": 'b', "text": 'Виноград.'},
            {"label": 'c', "text": 'Оливки.'},
        ],
    },
    4025: {
        "question": 'Какая женщина является автором картины «Вербена»?',
        "answer": 'Маруха Мальо.',
        "options": [
            {"label": 'a', "text": 'Маруха Мальо.'},
            {"label": 'b', "text": 'Кармен Маура.'},
            {"label": 'c', "text": 'Клара Лаго.'},
        ],
    },
    4026: {
        "question": 'В каком испанском музее можно увидеть картину Пикассо «Герника»?',
        "answer": 'Музей королевы Софии.',
        "options": [
            {"label": 'a', "text": 'Музей Прадо.'},
            {"label": 'b', "text": 'Музей королевы Софии.'},
            {"label": 'c', "text": 'Музей Тиссен-Борнемиса.'},
        ],
    },
    4027: {
        "question": 'Какая испанская писательница пишет на другом официальном языке Испании?',
        "answer": 'Мерсе Родореда.',
        "options": [
            {"label": 'a', "text": 'Мерсэ Родореда.'},
            {"label": 'b', "text": 'Алмудена Гранде.'},
            {"label": 'c', "text": 'Ана Мария Матуте.'},
        ],
    },
    4028: {
        "question": 'Какие три культуры сосуществовали в средневековой Испании?',
        "answer": 'Христианская, иудейская и мусульманская.',
        "options": [
            {"label": 'a', "text": 'Христианка, еврейка и мусульманка.'},
            {"label": 'b', "text": 'Финикийка, еврейка и мусульманка.'},
            {"label": 'c', "text": 'Гречанка, христианка и еврейка.'},
        ],
    },
    4029: {
        "question": '6 декабря в Испании отмечается…',
        "answer": 'День Конституции.',
        "options": [
            {"label": 'a', "text": 'День Конституции.'},
            {"label": 'b', "text": 'приход Колумба в Америку.'},
            {"label": 'c', "text": 'День книги.'},
        ],
    },
    4030: {
        "question": 'Какой город был научным центром в Аль-Андалусе, где изучали медицину и астрономию?',
        "answer": 'Кордова.',
        "options": [
            {"label": 'a', "text": 'Барселона.'},
            {"label": 'b', "text": 'Мадрид.'},
            {"label": 'c', "text": 'Кórdoba.'},
        ],
    },
    4031: {
        "question": 'В каком испанском городе находится музей Гуггенхайма?',
        "answer": 'Бильбао.',
        "options": [
            {"label": 'a', "text": 'Бильбао.'},
            {"label": 'b', "text": 'Мадрид.'},
            {"label": 'c', "text": 'Валенсия.'},
        ],
    },
    4032: {
        "question": 'Премия Сервантеса присуждается…',
        "answer": 'писателям.',
        "options": [
            {"label": 'a', "text": 'актеры.'},
            {"label": 'b', "text": 'писатели'},
            {"label": 'c', "text": 'художники.'},
        ],
    },
    4033: {
        "question": 'Какая премия присуждается лучшим актёрам и фильмам?',
        "answer": 'Премия Гойя.',
        "options": [
            {"label": 'a', "text": 'Премия Гойя.'},
            {"label": 'b', "text": 'Нобелевская премия.'},
            {"label": 'c', "text": 'Премия Сервантеса.'},
        ],
    },
    4034: {
        "question": 'Какие премии продвигают научные, культурные и гуманистические ценности в Испании?',
        "answer": 'Премии принцессы Астурийской.',
        "options": [
            {"label": 'a', "text": 'Премия Сервантеса.'},
            {"label": 'b', "text": 'Премия Принцессы Астурийской.'},
            {"label": 'c', "text": 'Премия Гойя.'},
        ],
    },
    4035: {
        "question": 'Какой из этих видов спорта очень популярен в Испании?',
        "answer": 'Футбол.',
        "options": [
            {"label": 'a', "text": 'Футбол.'},
            {"label": 'b', "text": 'Лыжи'},
            {"label": 'c', "text": 'Гольф.'},
        ],
    },
    4036: {
        "question": 'Кто из этих спортсменов играет в теннис?',
        "answer": 'Карлос Алькарас.',
        "options": [
            {"label": 'a', "text": 'Пау Газоль.'},
            {"label": 'b', "text": 'Карлос Сайнс.'},
            {"label": 'c', "text": 'Карлос Алькарас.'},
        ],
    },
    5001: {
        "question": 'Какой документ должны получить иностранцы для легального проживания в Испании?',
        "answer": 'Удостоверение личности иностранца (TIE).',
        "options": [
            {"label": 'a', "text": 'Национальный документ удостоверяющий личность (DNI).'},
            {"label": 'b', "text": 'Карточка идентификации иностранца (TIE).'},
            {"label": 'c', "text": 'Сертификат о регистрации по месту жительства.'},
        ],
    },
    5002: {
        "question": 'Какой документ подтверждает место жительства владельца?',
        "answer": 'Справка о регистрации по месту жительства.',
        "options": [
            {"label": 'a', "text": 'Сертификат о регистрации по месту жительства.'},
            {"label": 'b', "text": 'Свидетельство о рождении.'},
            {"label": 'c', "text": 'Водительские права.'},
        ],
    },
    5003: {
        "question": 'Что заменяет индивидуальный электронный реестр?',
        "answer": 'Семейную книгу.',
        "options": [
            {"label": 'a', "text": 'К DNI.'},
            {"label": 'b', "text": 'К водительским правам.'},
            {"label": 'c', "text": 'К семейной книге.'},
        ],
    },
    5004: {
        "question": 'Каков минимальный возраст для вождения автомобиля в Испании?',
        "answer": '18 лет.',
        "options": [
            {"label": 'a', "text": '16 лет.'},
            {"label": 'b', "text": '18 лет.'},
            {"label": 'c', "text": '20 лет.'},
        ],
    },
    5005: {
        "question": 'Где получают водительские права?',
        "answer": 'В Главном управлении дорожного движения (DGT).',
        "options": [
            {"label": 'a', "text": 'Генеральная дирекция дорожного движения (DGT).'},
            {"label": 'b', "text": 'Национальная полиция.'},
            {"label": 'c', "text": 'Гражданский регистр.'},
        ],
    },
    5006: {
        "question": 'Для получения водительских прав нужно сдать…',
        "answer": 'теоретический и практический экзамены.',
        "options": [
            {"label": 'a', "text": 'теоретический экзамен.'},
            {"label": 'b', "text": 'практический экзамен.'},
            {"label": 'c', "text": 'теоретический экзамен и практический экзамен.'},
        ],
    },
    5007: {
        "question": 'Где оформляется семейная книга?',
        "answer": 'В ЗАГСе.',
        "options": [
            {"label": 'a', "text": 'В ЗАГСе.'},
            {"label": 'b', "text": 'В социальном обеспечении.'},
            {"label": 'c', "text": 'В полицейских участках.'},
        ],
    },
    5008: {
        "question": 'Какой из этих телеканалов является региональным?',
        "answer": 'Canal Sur.',
        "options": [
            {"label": 'a', "text": 'Телесинко.'},
            {"label": 'b', "text": 'Нова.'},
            {"label": 'c', "text": 'Канал Сур.'},
        ],
    },
    5009: {
        "question": 'Сколько длится отпуск по материнству или отцовству?',
        "answer": '16 недель.',
        "options": [
            {"label": 'a', "text": '12 недель.'},
            {"label": 'b', "text": '16 недель.'},
            {"label": 'c', "text": '22 недели.'},
        ],
    },
    5010: {
        "question": 'Каков максимально допустимый уровень алкоголя в крови для водителей (г/л)?',
        "answer": '0,5.',
        "options": [
            {"label": 'a', "text": '0,5.'},
            {"label": 'b', "text": '0,7.'},
            {"label": 'c', "text": '0,9.'},
        ],
    },
    5011: {
        "question": 'Какой тип жилья наиболее распространён в Испании?',
        "answer": 'Квартира в многоквартирном доме.',
        "options": [
            {"label": 'a', "text": 'Сельский дом.'},
            {"label": 'b', "text": 'Квартира в жилом здании.'},
            {"label": 'c', "text": 'Отдельный шале.'},
        ],
    },
    5012: {
        "question": 'Какое автономное сообщество известно качеством оливкового масла?',
        "answer": 'Андалусия.',
        "options": [
            {"label": 'a', "text": 'Кантабрия.'},
            {"label": 'b', "text": 'Андалусия.'},
            {"label": 'c', "text": 'Ла Риоха.'},
        ],
    },
    5013: {
        "question": 'Как называется обязательный технический осмотр автомобилей?',
        "answer": 'ITV (Техническая инспекция транспортных средств).',
        "options": [
            {"label": 'a', "text": 'IBI (Налог на недвижимое имущество).'},
            {"label": 'b', "text": 'ITV (Технический осмотр транспортных средств).'},
            {"label": 'c', "text": 'ИТЕ (Техническая инспекция зданий).'},
        ],
    },
    5014: {
        "question": 'Как называется закуска, которую подают к напитку в барах и ресторанах?',
        "answer": 'Тапа.',
        "options": [
            {"label": 'a', "text": 'бутерброд'},
            {"label": 'b', "text": 'крышка'},
            {"label": 'c', "text": 'первое блюдо'},
        ],
    },
    5015: {
        "question": 'Где оформляется медицинская карта?',
        "answer": 'В поликлинике.',
        "options": [
            {"label": 'a', "text": 'В полицейском участке.'},
            {"label": 'b', "text": 'В центре здоровья.'},
            {"label": 'c', "text": 'В Министерстве здравоохранения.'},
        ],
    },
    5016: {
        "question": 'С каким количеством детей семья считается многодетной?',
        "answer": 'С 3 детьми.',
        "options": [
            {"label": 'a', "text": 'С одним ребенком.'},
            {"label": 'b', "text": 'С двумя детьми.'},
            {"label": 'c', "text": 'С тремя детьми.'},
        ],
    },
    5017: {
        "question": 'В Испании разрешён брак…',
        "answer": 'между людьми одного и разного пола.',
        "options": [
            {"label": 'a', "text": 'только между людьми одного пола.'},
            {"label": 'b', "text": 'между людьми одного и разного пола.'},
            {"label": 'c', "text": 'только между людьми разного пола.'},
        ],
    },
    5018: {
        "question": 'Владельцы собак должны регистрировать их в…',
        "answer": 'муниципалитете.',
        "options": [
            {"label": 'a', "text": 'Министерство юстиции.'},
            {"label": 'b', "text": 'полицейский участок'},
            {"label": 'c', "text": 'Городской совет.'},
        ],
    },
    5019: {
        "question": 'Основные ингредиенты испанского омлета — яйца и…',
        "answer": 'картофель.',
        "options": [
            {"label": 'a', "text": 'перцы'},
            {"label": 'b', "text": 'картофель'},
            {"label": 'c', "text": 'помидоры.'},
        ],
    },
    5020: {
        "question": 'Какое блюдо испанской кухни наиболее известно в мире?',
        "answer": 'Гаспачо.',
        "options": [
            {"label": 'a', "text": 'Гаспачо.'},
            {"label": 'b', "text": 'Пицца.'},
            {"label": 'c', "text": 'Паста.'},
        ],
    },
    5021: {
        "question": 'Какой из этих телеканалов является государственным?',
        "answer": 'La 1.',
        "options": [
            {"label": 'a', "text": 'Телевизионный канал 5.'},
            {"label": 'b', "text": 'Ла 1.'},
            {"label": 'c', "text": 'Антена 3.'},
        ],
    },
    5022: {
        "question": 'Одно из правил в жилищном товариществе — это…',
        "answer": 'не шуметь.',
        "options": [
            {"label": 'a', "text": 'открыть дверь почтальону.'},
            {"label": 'b', "text": 'Не беспокоить шумом.'},
            {"label": 'c', "text": 'убирать общие пространства.'},
        ],
    },
    5023: {
        "question": 'Какой основной ингредиент валенсийской паэльи?',
        "answer": 'Рис.',
        "options": [
            {"label": 'a', "text": 'Рис.'},
            {"label": 'b', "text": 'Чоризо.'},
            {"label": 'c', "text": 'Нут.'},
        ],
    },
    5024: {
        "question": 'Сидр — типичный напиток…',
        "answer": 'Астурии.',
        "options": [
            {"label": 'a', "text": 'Астурия.'},
            {"label": 'b', "text": 'Валенсия.'},
            {"label": 'c', "text": 'Канары.'},
        ],
    },
    5025: {
        "question": 'У испанцев две фамилии, первая…',
        "answer": 'может быть от матери или отца.',
        "options": [
            {"label": 'a', "text": 'обязательно матери.'},
            {"label": 'b', "text": 'обязательно отца.'},
            {"label": 'c', "text": 'Это может быть мать или отец.'},
        ],
    },
    5026: {
        "question": 'Национальный праздник Испании —…',
        "answer": '12 октября.',
        "options": [
            {"label": 'a', "text": '6 декабря.'},
            {"label": 'b', "text": '15 августа.'},
            {"label": 'c', "text": '12 октября.'},
        ],
    },
    5027: {
        "question": 'В какие дни обычно закрыты большинство магазинов?',
        "answer": 'В воскресенье.',
        "options": [
            {"label": 'a', "text": 'Понедельники.'},
            {"label": 'b', "text": 'В воскресенья.'},
            {"label": 'c', "text": 'Субботними afternoons.'},
        ],
    },
    5028: {
        "question": 'Где оформляется паспорт?',
        "answer": 'В полицейском участке.',
        "options": [
            {"label": 'a', "text": 'В ЗАГСе.'},
            {"label": 'b', "text": 'В полицейском участке.'},
            {"label": 'c', "text": 'В мэрии.'},
        ],
    },
    5029: {
        "question": 'Министерство равноправия борется с гендерным насилием и…',
        "answer": 'дискриминацией.',
        "options": [
            {"label": 'a', "text": 'разделение'},
            {"label": 'b', "text": 'дискриминация.'},
            {"label": 'c', "text": 'солидарность'},
        ],
    },
    5030: {
        "question": 'Какое автономное сообщество известно качеством своих кав?',
        "answer": 'Каталония.',
        "options": [
            {"label": 'a', "text": 'Галисия.'},
            {"label": 'b', "text": 'Каталония.'},
            {"label": 'c', "text": 'Кастилия-Ла-Манча.'},
        ],
    },
    5031: {
        "question": 'Какой документ нужен для получения медицинской помощи в государственной системе?',
        "answer": 'Медицинская карта.',
        "options": [
            {"label": 'a', "text": 'Паспорт.'},
            {"label": 'b', "text": 'Медицинская карта.'},
            {"label": 'c', "text": 'Свидетельство о рождении.'},
        ],
    },
    5032: {
        "question": 'Время на Канарских островах по сравнению с полуостровом…',
        "answer": 'на час меньше.',
        "options": [
            {"label": 'a', "text": 'Два часа меньше.'},
            {"label": 'b', "text": 'На час меньше.'},
            {"label": 'c', "text": 'один час больше.'},
        ],
    },
    5033: {
        "question": 'Для поступления в университет нужно сдать экзамен под названием…',
        "answer": 'Вступительный экзамен в университет.',
        "options": [
            {"label": 'a', "text": 'Выборность.'},
            {"label": 'b', "text": 'Предуниверситетский экзамен.'},
            {"label": 'c', "text": 'Экзамен для поступления в университет.'},
        ],
    },
    5034: {
        "question": 'Какой из этих продуктов Испания импортирует из других стран?',
        "answer": 'Нефть.',
        "options": [
            {"label": 'a', "text": 'Нефть.'},
            {"label": 'b', "text": 'Оливковое масло.'},
            {"label": 'c', "text": 'Лекарства.'},
        ],
    },
    5035: {
        "question": 'Какие налоги должны платить граждане в Испании?',
        "answer": 'Прямые и косвенные налоги.',
        "options": [
            {"label": 'a', "text": 'Прямые налоги, такие как НДФЛ.'},
            {"label": 'b', "text": 'Косвенные налоги, такие как НДС.'},
            {"label": 'c', "text": 'Прямые и косвенные налоги.'},
        ],
    },
    5036: {
        "question": 'Взрослые без аттестата о среднем образовании могут поступить в университет, сдав специальный экзамен с…',
        "answer": '25 лет.',
        "options": [
            {"label": 'a', "text": '18 лет.'},
            {"label": 'b', "text": '23 года.'},
            {"label": 'c', "text": '25 лет.'},
        ],
    },
    5037: {
        "question": 'Где можно встретить правило «Не ходить по газону, не рвать цветы»?',
        "answer": 'В зонах отдыха.',
        "options": [
            {"label": 'a', "text": 'В зонах отдыха.'},
            {"label": 'b', "text": 'В театрах.'},
            {"label": 'c', "text": 'На футбольных стадионах.'},
        ],
    },
    5038: {
        "question": 'Бакалавриат в Испании…',
        "answer": 'состоит из двух академических курсов.',
        "options": [
            {"label": 'a', "text": 'это обязательно.'},
            {"label": 'b', "text": 'Состоит из двух академических курсов.'},
            {"label": 'c', "text": 'Это обучение учеников 14-16 лет.'},
        ],
    },
    5039: {
        "question": 'Налог на добавленную стоимость (НДС) относится к…',
        "answer": 'косвенным налогам.',
        "options": [
            {"label": 'a', "text": 'Косвенные налоги.'},
            {"label": 'b', "text": 'Налог на доходы.'},
            {"label": 'c', "text": 'Налоги на прибыль.'},
        ],
    },
    5040: {
        "question": 'Какой номер получают работники при первом трудоустройстве?',
        "answer": 'Номер социального страхования.',
        "options": [
            {"label": 'a', "text": 'Социального обеспечения.'},
            {"label": 'b', "text": 'Паспорт.'},
            {"label": 'c', "text": 'Номер обслуживания.'},
        ],
    },
    5041: {
        "question": 'Государственные школы…',
        "answer": 'бесплатные.',
        "options": [
            {"label": 'a', "text": 'они могут решить количество мест.'},
            {"label": 'b', "text": 'Они могут нанимать любых преподавателей, которых захотят.'},
            {"label": 'c', "text": 'они бесплатные.'},
        ],
    },
    5042: {
        "question": 'Какой из этих портов является одним из главных в Испании?',
        "answer": 'Альхесирас.',
        "options": [
            {"label": 'a', "text": 'Тенерифе.'},
            {"label": 'b', "text": 'Аликанте.'},
            {"label": 'c', "text": 'Алхесирас.'},
        ],
    },
    5043: {
        "question": 'Частная школа с государственным финансированием — это школа, которая…',
        "answer": 'получает деньги от государства.',
        "options": [
            {"label": 'a', "text": 'получает деньги от администрации.'},
            {"label": 'b', "text": 'финансируют родители учеников.'},
            {"label": 'c', "text": 'получает деньги от банков.'},
        ],
    },
    5044: {
        "question": 'Испания экспортирует продукцию в основном в страны…',
        "answer": 'Европейского союза.',
        "options": [
            {"label": 'a', "text": 'из Испаноамерики.'},
            {"label": 'b', "text": 'из Европейского Союза.'},
            {"label": 'c', "text": 'северной Африки.'},
        ],
    },
    5045: {
        "question": 'Публичные библиотеки бесплатны для…',
        "answer": 'всех.',
        "options": [
            {"label": 'a', "text": 'все.'},
            {"label": 'b', "text": 'безработные'},
            {"label": 'c', "text": 'дети.'},
        ],
    },
    5046: {
        "question": 'Какой из этих продуктов Испания экспортирует больше, чем импортирует?',
        "answer": 'Обувь.',
        "options": [
            {"label": 'a', "text": 'Газ.'},
            {"label": 'b', "text": 'Одежда.'},
            {"label": 'c', "text": 'Обувь.'},
        ],
    },
    5047: {
        "question": 'Лицо старше 18 лет может получить аттестат об обязательном среднем образовании в…',
        "answer": 'Центре образования для взрослых.',
        "options": [
            {"label": 'a', "text": 'Центр образования для взрослых.'},
            {"label": 'b', "text": 'начальная школа'},
            {"label": 'c', "text": 'университет'},
        ],
    },
    5048: {
        "question": 'Профессиональное образование…',
        "answer": 'может быть среднего или высшего уровня.',
        "options": [
            {"label": 'a', "text": 'Это для людей старше 25 лет.'},
            {"label": 'b', "text": 'может быть среднего или высшего уровня.'},
            {"label": 'c', "text": 'Это обязательно.'},
        ],
    },
    5049: {
        "question": 'Куда мы идём к семейному врачу или педиатру?',
        "answer": 'В поликлинику.',
        "options": [
            {"label": 'a', "text": 'В больницу.'},
            {"label": 'b', "text": 'В центр здоровья.'},
            {"label": 'c', "text": 'В аптеку.'},
        ],
    },
    5050: {
        "question": 'На сколько лет действительна европейская медицинская карта?',
        "answer": 'На два года.',
        "options": [
            {"label": 'a', "text": 'На год.'},
            {"label": 'b', "text": 'На два года.'},
            {"label": 'c', "text": 'На 10 лет.'},
        ],
    },
    5051: {
        "question": 'Во сколько обычно ужинают в Испании?',
        "answer": 'В 21 или 22 часа.',
        "options": [
            {"label": 'a', "text": 'В 18:00.'},
            {"label": 'b', "text": 'В 23 часа.'},
            {"label": 'c', "text": 'В 21 или 22 часа.'},
        ],
    },
    5052: {
        "question": 'Какой единый телефонный номер для любой экстренной ситуации?',
        "answer": '112.',
        "options": [
            {"label": 'a', "text": '060.'},
            {"label": 'b', "text": '112.'},
            {"label": 'c', "text": '911'},
        ],
    },
    5053: {
        "question": 'Какая из этих газет издаётся на национальном уровне?',
        "answer": 'El País.',
        "options": [
            {"label": 'a', "text": 'Эль Диа́рио Васко.'},
            {"label": 'b', "text": 'Эль Паис.'},
            {"label": 'c', "text": 'Голос Галисии.'},
        ],
    },
    5054: {
        "question": 'Где продаются марки и табак?',
        "answer": 'В табачном киоске.',
        "options": [
            {"label": 'a', "text": 'В киоске.'},
            {"label": 'b', "text": 'В аптеке.'},
            {"label": 'c', "text": 'В табачной лавке.'},
        ],
    },
    5055: {
        "question": 'Когда можно позвонить на телефон помощи жертвам гендерного насилия?',
        "answer": 'Круглосуточно.',
        "options": [
            {"label": 'a', "text": '24 часа в сутки.'},
            {"label": 'b', "text": 'В утреннее время.'},
            {"label": 'c', "text": 'С понедельника по пятницу.'},
        ],
    },
    5056: {
        "question": 'Организация, работающая над интеграцией людей с нарушениями зрения, — это…',
        "answer": 'ONCE.',
        "options": [
            {"label": 'a', "text": 'ОНСЕ.'},
            {"label": 'b', "text": 'ЮНИСЕФ.'},
            {"label": 'c', "text": 'Караитас.'},
        ],
    },
    5057: {
        "question": 'Путь Святого Иакова — это…',
        "answer": 'объект Всемирного наследия.',
        "options": [
            {"label": 'a', "text": 'Объект Всемирного наследия.'},
            {"label": 'b', "text": 'железнодорожная линия'},
            {"label": 'c', "text": 'маршрут для туристов'},
        ],
    },
    5058: {
        "question": 'Какой государственный телеканал круглосуточно транслирует новости?',
        "answer": 'Canal 24 horas.',
        "options": [
            {"label": 'a', "text": 'Теледепорте.'},
            {"label": 'b', "text": 'Ла 1.'},
            {"label": 'c', "text": 'Канал 24 часа.'},
        ],
    },
    5059: {
        "question": 'Бесплатный телефон для жертв гендерного насилия —…',
        "answer": '016.',
        "options": [
            {"label": 'a', "text": '091.'},
            {"label": 'b', "text": '112.'},
            {"label": 'c', "text": '016.'},
        ],
    },
    5060: {
        "question": 'В Испании железнодорожная сеть бывает дальнего, среднего следования и…',
        "answer": 'пригородной.',
        "options": [
            {"label": 'a', "text": 'пригородный'},
            {"label": 'b', "text": 'сельский'},
            {"label": 'c', "text": 'транснациональный'},
        ],
    },
    5061: {
        "question": 'Что запрещено у входа в школу?',
        "answer": 'Курить.',
        "options": [
            {"label": 'a', "text": 'Курить сигарету.'},
            {"label": 'b', "text": 'Водить машину.'},
            {"label": 'c', "text": 'Продавать безалкогольные напитки.'},
        ],
    },
    5062: {
        "question": 'Какой диплом получают после окончания среднего цикла профессионального образования?',
        "answer": 'Техник.',
        "options": [
            {"label": 'a', "text": 'Бакалавр.'},
            {"label": 'b', "text": 'Техник.'},
            {"label": 'c', "text": 'Выпускник ESO.'},
        ],
    },
    5063: {
        "question": 'Какую степень получают после защиты докторской диссертации в Испании?',
        "answer": 'Доктор.',
        "options": [
            {"label": 'a', "text": 'Магистр.'},
            {"label": 'b', "text": 'Выпускник.'},
            {"label": 'c', "text": 'Доктор.'},
        ],
    },
    5064: {
        "question": 'Где покупают лекарства по рецепту?',
        "answer": 'В аптеке.',
        "options": [
            {"label": 'a', "text": 'В больнице'},
            {"label": 'b', "text": 'В центре здоровья.'},
            {"label": 'c', "text": 'В аптеке.'},
        ],
    },
    5065: {
        "question": 'Какую из этих рекомендаций можно встретить в парке?',
        "answer": 'Не ходить по газону.',
        "options": [
            {"label": 'a', "text": 'Не ходить по траве.'},
            {"label": 'b', "text": 'Рекомендуется оплачивать билет точной суммой.'},
            {"label": 'c', "text": 'Соблюдать правила по багажу.'},
        ],
    },
    5066: {
        "question": 'Что обязательно для владельца автомобиля в Испании?',
        "answer": 'Страховка.',
        "options": [
            {"label": 'a', "text": 'Гараж'},
            {"label": 'b', "text": 'Страхование.'},
            {"label": 'c', "text": 'Сигнализация.'},
        ],
    },
    5067: {
        "question": 'Аэропорт Адольфо Суарес находится в…',
        "answer": 'Мадриде.',
        "options": [
            {"label": 'a', "text": 'Барселона.'},
            {"label": 'b', "text": 'Мадрид'},
            {"label": 'c', "text": 'Бильбао.'},
        ],
    },
    5068: {
        "question": 'В автомобиле ремень безопасности обязателен...',
        "answer": 'на всех сиденьях.',
        "options": [
            {"label": 'a', "text": 'только на водительском сиденье.'},
            {"label": 'b', "text": 'на передних сиденьях.'},
            {"label": 'c', "text": 'на всех местах.'},
        ],
    },
    5069: {
        "question": 'Каков предел скорости на автомагистрали?',
        "answer": '120 км/ч.',
        "options": [
            {"label": 'a', "text": '90 км/ч.'},
            {"label": 'b', "text": '120 км/ч.'},
            {"label": 'c', "text": '150 км/ч.'},
        ],
    },
    5070: {
        "question": 'Уступать место людям с ограниченной подвижностью — правило, которое встречается в…',
        "answer": 'общественном транспорте.',
        "options": [
            {"label": 'a', "text": 'общественный транспорт.'},
            {"label": 'b', "text": 'библиотеки.'},
            {"label": 'c', "text": 'музеи.'},
        ],
    },
    5071: {
        "question": 'Какой вид общественного транспорта имеет зелёный огонёк, когда свободен?',
        "answer": 'Такси.',
        "options": [
            {"label": 'a', "text": 'Автобус.'},
            {"label": 'b', "text": 'Такси.'},
            {"label": 'c', "text": 'Трамвай.'},
        ],
    },
    5072: {
        "question": 'Что нужно делать, если у вас есть собака?',
        "answer": 'Чипировать и вакцинировать её.',
        "options": [
            {"label": 'a', "text": 'Выгуливать без поводка.'},
            {"label": 'b', "text": 'Поставить микрочип и вакцинировать его.'},
            {"label": 'c', "text": 'Не собирать их экскременты.'},
        ],
    },
    5073: {
        "question": 'Испанцам нужен паспорт для поездки в…',
        "answer": 'Китай.',
        "options": [
            {"label": 'a', "text": 'Италия.'},
            {"label": 'b', "text": 'Китай.'},
            {"label": 'c', "text": 'Германия.'},
        ],
    },
    5074: {
        "question": 'Каков минимальный возраст для работы в Испании?',
        "answer": '16 лет.',
        "options": [
            {"label": 'a', "text": '16 лет.'},
            {"label": 'b', "text": '18 лет.'},
            {"label": 'c', "text": '21 лет.'},
        ],
    },
    5075: {
        "question": 'Какой сектор имеет наибольший вес в испанской экономике?',
        "answer": 'Услуги.',
        "options": [
            {"label": 'a', "text": 'Сельское хозяйство.'},
            {"label": 'b', "text": 'Услуги.'},
            {"label": 'c', "text": 'Строительство.'},
        ],
    },
    5076: {
        "question": 'Испания является инновационной в секторе…',
        "answer": 'возобновляемых источников энергии.',
        "options": [
            {"label": 'a', "text": 'аэрокосмическая инженерия.'},
            {"label": 'b', "text": 'возобновляемые источники энергии.'},
            {"label": 'c', "text": 'ядерная энергия.'},
        ],
    },
    5077: {
        "question": 'Как называется главный трудовой закон Испании?',
        "answer": 'Статут трудящихся.',
        "options": [
            {"label": 'a', "text": 'Конституция.'},
            {"label": 'b', "text": 'Статут работников.'},
            {"label": 'c', "text": 'Государственная служба занятости.'},
        ],
    },
    5078: {
        "question": 'Какое из этих заведений работает круглосуточно при необходимости?',
        "answer": 'Аптека.',
        "options": [
            {"label": 'a', "text": 'Аптека.'},
            {"label": 'b', "text": 'Рыбный магазин.'},
            {"label": 'c', "text": 'Книжный магазин.'},
        ],
    },
    5079: {
        "question": 'Дошкольное образование в Испании…',
        "answer": 'имеет два цикла.',
        "options": [
            {"label": 'a', "text": 'это обязательно.'},
            {"label": 'b', "text": 'имеет два цикла.'},
            {"label": 'c', "text": 'начинается в 4 года.'},
        ],
    },
    5080: {
        "question": 'Когда начинается учебный год?',
        "answer": 'В сентябре.',
        "options": [
            {"label": 'a', "text": 'В августе.'},
            {"label": 'b', "text": 'В сентябре.'},
            {"label": 'c', "text": 'В октябре.'},
        ],
    },
    5081: {
        "question": 'Официальные языковые школы…',
        "answer": 'для лиц старше 16 лет.',
        "options": [
            {"label": 'a', "text": 'это частные учебные заведения.'},
            {"label": 'b', "text": 'Это для лиц старше 16 лет.'},
            {"label": 'c', "text": 'зависят от Института Сервантеса.'},
        ],
    },
    5082: {
        "question": 'Какой документ содержит информацию о стаже социальных отчислений?',
        "answer": 'Справка о трудовой деятельности.',
        "options": [
            {"label": 'a', "text": 'Справка о трудовой деятельности.'},
            {"label": 'b', "text": 'Квитанция о расчете.'},
            {"label": 'c', "text": 'Сертификат профессиональной квалификации.'},
        ],
    },
    5083: {
        "question": 'Коллективные договоры компании подписываются с представителями работников о…',
        "answer": 'условиях труда.',
        "options": [
            {"label": 'a', "text": 'условия труда'},
            {"label": 'b', "text": 'будущее компании.'},
            {"label": 'c', "text": 'отношения с клиентами.'},
        ],
    },
    5084: {
        "question": 'В каком из этих секторов выделяется Испания?',
        "answer": 'В туризме.',
        "options": [
            {"label": 'a', "text": 'В туризме.'},
            {"label": 'b', "text": 'В автомобильной промышленности.'},
            {"label": 'c', "text": 'В цифровых технологиях.'},
        ],
    },
}


# Task section titles
sections = {
    1: ("TAREA 1: Gobierno, legislación y participación ciudadana",
        "РАЗДЕЛ 1: Государственное управление, законодательство и участие граждан"),
    2: ("TAREA 2: Derechos y deberes fundamentales",
        "РАЗДЕЛ 2: Основные права и обязанности"),
    3: ("TAREA 3: Organización territorial de España. Geografía física y política",
        "РАЗДЕЛ 3: Территориальная организация Испании. Физическая и политическая география"),
    4: ("TAREA 4: Cultura e historia de España",
        "РАЗДЕЛ 4: Культура и история Испании"),
    5: ("TAREA 5: Sociedad española",
        "РАЗДЕЛ 5: Испанское общество"),
}

def get_section(q_num):
    if 1001 <= q_num <= 1120:
        return 1
    elif 2001 <= q_num <= 2036:
        return 2
    elif 3001 <= q_num <= 3024:
        return 3
    elif 4001 <= q_num <= 4036:
        return 4
    elif 5001 <= q_num <= 5084:
        return 5
    return 0

def generate_markdown():
    output = []
    output.append("# Preguntas CCSE 2026 / Вопросы CCSE 2026\n")
    output.append("---\n")

    current_section = 0

    for q_num in sorted(questions.keys()):
        section = get_section(q_num)
        if section != current_section:
            current_section = section
            es_title, ru_title = sections[section]
            output.append(f"\n## **{es_title}**\n")
            output.append(f"{ru_title}\n")
            output.append("---\n")

        es_q, es_a = questions[q_num]
        ru_q, ru_a = translations[q_num]

        output.append(f"\n### {q_num}\n")
        output.append(f"**{es_q}**\n")
        output.append(f"{ru_q}\n")
        output.append(f"\n**✓ {es_a}**\n")
        output.append(f"✓ {ru_a}\n")

    return "\n".join(output)

if __name__ == "__main__":
    content = generate_markdown()
    with open("ccse_preguntas_es_ru.md", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated file with {len(questions)} questions")
