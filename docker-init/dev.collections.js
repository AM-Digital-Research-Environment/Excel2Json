db = db.getSiblingDB("dev");
db.createCollection("dictionaries");

db.dictionaries.insertMany([
    {
        name: "MODS Top Level Elments",
        elements: {
            "0": "titleInfo",
            "1": "name",
            "2": "typeOfResource",
            "3": "genre",
            "4": "originInfo",
            "5": "language",
            "6": "physicalDescription",
            "7": "abstract",
            "8": "tableOfContents",
            "9": "targetAudience",
            "10": "note",
            "11": "subject",
            "12": "classification",
            "13": "relatedItem",
            "14": "identifier",
            "15": "location",
            "16": "accessCondition",
            "17": "part",
            "18": "extension",
            "19": "recordInfo",
        },
    },
    {
        name: "Field Names by Excel Table Tabs",
        tabs: {
            "1. General": {
                "0": "slno",
                "1": "filename",
                "2": "user_rights",
                "3": "users",
                "4": "security_level",
                "5": "security_level_desc",
                "6": "resource_type",
                "7": "collection",
                "8": "identifier_1",
                "9": "identifier_type_1",
                "10": "identifier_2",
                "11": "identifier_type_2",
                "12": "identifier_3",
                "13": "identifier_type_3",
                "14": "identifier_4",
                "15": "identifier_type_4",
                "16": "sponsor",
                "17": "citation",
                "18": "language",
                "19": "project_id",
                "20": "project_name",
                "21": "loc_origin_l1",
                "22": "loc_origin_l2",
                "23": "loc_origin_l3",
                "24": "current_location",
                "25": "url",
                "26": "use_copy_rights",
                "27": "target_aud",
                "28": "abstract",
                "29": "table_contents",
                "30": "note",
                "31": null,
            },
            "2. AssociatedPerson": {
                "0": "slno",
                "1": "filename",
                "2": "role_1",
                "3": "name_1",
                "4": "affl_1",
                "5": "role_2",
                "6": "name_2",
                "7": "affl_2",
                "8": "role_3",
                "9": "name_3",
                "10": "affl_3",
                "11": "role_4",
                "12": "name_4",
                "13": "affl_4",
                "14": "role_5",
                "15": "name_5",
                "16": "affl_5",
                "17": "role_6",
                "18": "name_6",
                "19": "affl_6",
                "20": "role_7",
                "21": "name_7",
                "22": "affl_7",
                "23": "role_8",
                "24": "name_8",
                "25": "affl_8",
                "26": "role_9",
                "27": "name_9",
                "28": "affl_9",
                "29": "role_10",
                "30": "name_10",
                "31": "affl_10",
            },
            "3. Title+Date": {
                "0": "slno",
                "1": "filename",
                "2": "title_main",
                "3": "title_2",
                "4": "title_type_2",
                "5": "title_3",
                "6": "title_type_3",
                "7": "title_4",
                "8": "title_type_4",
                "9": "title_5",
                "10": "title_type_5",
                "11": "date_issue",
                "12": "date_created",
                "13": "date_captured",
                "14": "date_valid",
                "15": "date_mod",
                "16": "date_copy",
                "17": "date_other",
                "18": "date_disp",
                "19": null,
                "20": null,
                "21": null,
                "22": null,
                "23": null,
                "24": null,
                "25": null,
                "26": null,
                "27": null,
                "28": null,
                "29": null,
                "30": null,
                "31": null,
            },
            "4. Description+Genre": {
                "0": "slno",
                "1": "filename",
                "2": "physical_type",
                "3": "dig_method",
                "4": "physical_desc",
                "5": "physical_tech",
                "6": "physical_desc_note",
                "7": "genre_marc",
                "8": "genre_loc",
                "9": "genre_aat",
                "10": "genre_tgm2",
                "11": "genre_none",
                "12": null,
                "13": null,
                "14": null,
                "15": null,
                "16": null,
                "17": null,
                "18": null,
                "19": null,
                "20": null,
                "21": null,
                "22": null,
                "23": null,
                "24": null,
                "25": null,
                "26": null,
                "27": null,
                "28": null,
                "29": null,
                "30": null,
                "31": null,
            },
            "5. RelatedItems": {
                "0": "slno",
                "1": "filename",
                "2": "subject",
                "3": "tags",
                "4": "rel_prec",
                "5": "rel_succ",
                "6": "rel_orig",
                "7": "rel_host",
                "8": "rel_cnst",
                "9": "rel_sers",
                "10": "rel_over",
                "11": "rel_otfo",
                "12": "rel_refc",
                "13": "rel_revi",
                "14": null,
                "15": null,
                "16": null,
                "17": null,
                "18": null,
                "19": null,
                "20": null,
                "21": null,
                "22": null,
                "23": null,
                "24": null,
                "25": null,
                "26": null,
                "27": null,
                "28": null,
                "29": null,
                "30": null,
                "31": null,
            },
        },
    },
    {
        name: "Tab Names",
        tabs: {
            "0": "1. General",
            "1": "2. AssociatedPerson",
            "2": "3. Title+Date",
            "3": "4. Description+Genre",
            "4": "5. RelatedItems",
        },
    },
    {
        name: "MODS to DC Identifier Mapping",
        data: {
            UserDefined: "local",
            Other: "other",
            "AGORHA (Accès global et organisé aux ressources en histoire de l'art)":
                "other",
            "AGROVOC multilingual agricultural thesaurus": "other",
            AllMovie: "other",
            AllMusic: "other",
            AlloCiné: "other",
            "American National Biography Online": "other",
            "American National Standards Institute and National Information Standards \nOrganisation number for an ANSI or ANSI/NISO standard":
                "other",
            "archINFORM index of locations": "other",
            "archINFORM index of persons": "other",
            "archINFORM projects": "other",
            "Archnet authorities": "other",
            "Archnet sites": "other",
            "Archival resource key (ARK) identifiers": "other",
            Artsy: "other",
            "Art UK artists": "other",
            "Art UK artworks": "other",
            "Agricultural thesaurus and glossary": "other",
            "BALaT (Belgian art links and tools) People & institutions":
                "other",
            "BBC things": "other",
            "Biographical directory of the United States Congress": "other",
            "Buddhist Digital Resource Center": "other",
            "Belvedere Künstler": "other",
            "Belvedere Werke": "other",
            "Benezit dictionary of artists": "other",
            "Biographies of the entomologists of the world": "other",
            "BFI - British Film Institute": "other",
            "BIBBI autoriteter": "other",
            "Большая российская энциклопедия = Bolʹshai︠a︡ rossiĭskai︠a︡ \nėnt︠s︡iklopedii︠a︡ (Great Russian Encyclopedia)":
                "other",
            "BnF catalogue général": "other",
            "Biografisch Portaal van Nederland": "other",
            "British Standards Institution": "other",
            "CABI thesaurus": "other",
            "Canadiana Authorities": "other",
            "CANTIC (Catàleg d'autoritats de noms i títols de Catalunya)":
                "other",
            "Collective biographies of women": "other",
            "CERL thesaurus": "other",
            "Canadian geographical names database": "other",
            "Clara: database of women artists": "other",
            "Quan guo bao kan suo yin (CNBKSY)": "other",
            "Cesko-Slovenská filmová databáze": "other",
            Danacode: "other",
            "Digital atlas of the Roman Empire": "other",
            "datos.bne.es": "other",
            Discogs: "other",
            "Det Danske Filminstitut Filmdatabasen": "other",
            "Digital musikkarkiv": "other",
            "Digital object identifier": "doi",
            "Dictionnaire des peintres belges": "other",
            "International article number": "other",
            "European case law identifier": "other",
            "EIDR: entertainment identifier registry": "other",
            "Digital platform for manuscript material from Swiss libraries and archives":
                "other",
            "Early modern letters online": "other",
            "The platform for digitized rare books from Swiss institutions":
                "other",
            "FAST - faceted application of subject terminology": "other",
            "Fide Chess Profile": "other",
            "Film Affinity": "other",
            "filmportal.de": "other",
            "Find a grave": "other",
            "FIS athlete": "other",
            Freebase: "other",
            "Fundació per a la Universitat Oberta de Catalunya (FUOC) product identifier":
                "other",
            "Global Agricultural Concept Scheme (GACS)": "other",
            "Gran enciclopèdia catalana": "other",
            "Geographic Names Database": "other",
            GeoNames: "other",
            "GEPRIS Historisch ID (Person)": "other",
            "Art & architecture thesaurus online": "other",
            "J. Paul Getty Museum artists": "other",
            "J. Paul Getty Museum objects": "other",
            "Getty thesaurus of geographic names online": "other",
            "Union list of artist names online": "other",
            "Gemeinsame Normdatei": "other",
            "Geographic Names Information System (GNIS)": "other",
            "Goodreads authors": "other",
            "Gemeenschappelijke Thesaurus Audiovisuele Archieven": "other",
            "Global Trade Identification Number 14 (EAN/UCC-128 or ITF-14)":
                "other",
            Handle: "other",
            "World Athletics": "other",
            "IBDB - Internet Broadway database": "other",
            "Iconography authority": "other",
            Iconoclass: "other",
            "IdRef: identifiants et référentiels": "other",
            "ILO Thesaurus": "other",
            "IMDb - Internet Movie Database": "other",
            "International standard audiovisual number": "other",
            "International standard book number": "isbn",
            "International standard book number (the actionable ISBN)": "isbn",
            "ISBN (International standard book number) registrant element":
                "isbn",
            "Identificativo SBN": "isbn",
            "International standard music number": "other",
            "International standard name identifier": "other",
            "International Organization for Standardization number for an ISO standard":
                "other",
            "ISFDB author directory": "other",
            "ISFDB award directory": "other",
            "ISFDB magazine directory": "other",
            "ISFDB publisher directory": "other",
            "ISIL (International standard identifier for libraries and related \norganizations)":
                "other",
            "International standard recording code": "other",
            "International standard serial number": "issn",
            "Linking International standard serial number": "other",
            "Sound recording issue number": "other",
            "International standard text code": "other",
            "International standard musical work code": "other",
            "Catalogo italiano dei periodici (ACNP)": "other",
            "ITAR (Importtjeneste og autoritetsregistre)": "other",
            "Researcher Number of the Grants-in-Aid for Scientific Research (KAKENHI) \nProgram":
                "other",
            "Kunstindeks Danmark artist": "other",
            "Kunstindeks Danmark work": "other",
            "КиноПоиск = KinoPoisk": "other",
            "Russian National Heritage Registry for Books": "other",
            "Author ID of the Union Catalogue Database of Japanese Texts":
                "other",
            Kulturnav: "other",
            "Currículo Lattes": "other",
            "Library of Congress control number": "other",
            "Library of Congress Manuscript Division field of history codes":
                "other",
            "Legal entity identifier": "other",
            "Libraries Australia": "other",
            "Modern Hebrew Literature - a Bio-Bibliographical Lexicon (Lexicon of Modern \nHebrew Literature)":
                "other",
            "Locally defined identifier": "other",
            "Marine Gazetteer": "other",
            MANTO: "other",
            "Sound recording matrix number": "other",
            "Medical Subject Headings": "other",
            "Musée d'Orsay Catalogue des oeuvres fiche oeuvre": "other",
            "Museum of Modern Art": "other",
            "Musée d'Orsay Répertoire des artistes notice artiste": "other",
            "MovieMeter films": "other",
            "MovieMeter regisseurs": "other",
            Munzinger: "other",
            "Music Sales Classical": "other",
            "Publisher's music plate number": "other",
            "Publisher-assigned music number": "other",
            MusicBrainz: "other",
            "National Archives Catalog": "other",
            "The National Archives (Great Britain: The National Archives)":
                "other",
            "U.S. National Gazetteer Feature Name Identifier": "other",
            "National Gallery of Art": "other",
            "National Gallery of Victoria artist": "other",
            "National Gallery of Victoria work": "other",
            "Author Authority ID of NACSIS-CAT": "other",
            "NIPO (Número de Identificación de las Publicaciones Oficiales)":
                "other",
            "National Library of Greece": "other",
            "NNDB (Notable Names Database)": "other",
            "National Portrait Gallery": "other",
            "National Standard Text Code": "other",
            "New Zealand gazetteer of place names": "other",
            "Oxford Dictionary of National Biography": "other",
            "OFDb: Online-Filmdatenbank": "other",
            "ONIX (Online Information Exchange)": "other",
            OpenStreetMap: "other",
            "Open researcher and contributor identifier": "other",
            "Norwegian national organization number": "other",
            "Oxford biography index": "other",
            "Pacific Coast Architecture Database - buildings list": "other",
            "Pacific Coast Architecture Database - persons list": "other",
            "Pacific Coast Architecture Database - practices and firms":
                "other",
            PermID: "other",
            "PIC - Photographers' Identities Catalog": "other",
            "Pleiades: a gazetteer of past places": "other",
            "Personen uit de Nederlandse Thesaurus van Auteursnamen": "other",
            "PORT.hu": "other",
            Prabook: "other",
            ResearcherID: "other",
            RKDartists: "other",
            "Research Organization Registry": "other",
            "S2A3 Biographical Database of Southern African Science": "other",
            "Smithsonian American Art Museum": "other",
            "Scholar Universe": "other",
            Scope: "other",
            "Scopus author identifier": "other",
            "Serial item and contribution identifier": "other",
            "Science Museum Group People": "other",
            "Social Networks and Archival Context": "other",
            Spotify: "other",
            "Sports Reference: Baseball": "other",
            "Sports Reference: Basketball": "other",
            "Sports Reference: College Basketball": "other",
            "Sports Reference: College Football": "other",
            "Sports Reference: Hockey": "other",
            "Sports Reference: Olympic Sports": "other",
            "Sports Reference: Pro Football": "other",
            "Semantic Scholar (Author)": "other",
            "Publisher, distributor, or vendor stock number": "other",
            "Standard technical report number": "other",
            "Standard-Thesaurus Wirtschaft = STW thesaurus for economics":
                "other",
            "Svensk Filmdatabas": "other",
            "Tate Artist Identifier": "other",
            Theatricalia: "other",
            "Tesauros del Patrimonio Cultural de España": "other",
            Trove: "other",
            "UNBIS Thesaurus": "other",
            "UNESCO thesaurus = Thésaurus de l'UNESCO = Tesauro de la UNESCO":
                "other",
            "Universal product code": "other",
            "Uniform resource identifier": "other",
            "Uniform resource name": "other",
            "Verzeichnis der Drucke des 16. Jahrhunderts": "other",
            "Verzeichnis der Drucke des 17. Jahrhunderts": "other",
            "Verzeichnis der Drucke des 18. Jahrhunderts": "other",
            "VGMdb artists": "other",
            "Virtual International Authority File number": "other",
            "Publisher-assigned videorecording number": "other",
            Wikidata: "other",
            "Web NDL authorities": "other",
            "WorldCat Entities": "other",
            "X Games athletes": "other",
            "ZooBank (Authors)": "other",
        },
    },
    {
        name: "MODS to DC Resource Type Mapping",
        data: {
            "Artefact (Physical artifact, 3-dimensional object, etc.)":
                "Physical Object",
            "Audio (Music, Sound recording, etc.)": "Audio",
            "Notated music (Sheet music, Printed music, etc.)": "Other",
            "Cartographic (Maps, Atlas, Globe, Digital Map)": "Map",
            "Image (2D Image, Photograph, Still Image, 2-dimensional nonprojected graphic, Nonprojected graphic)":
                "Image",
            "Moving image (Motion Picture, Film, Video, Slide, etc.)":
                "Audiovisual (Presentation, Film, …)",
            Text: "Other",
            Manuscript: "Manuscript",
            Bibliography: "Other",
            "Dataset (table, graphs)": "Dataset",
            "Digital (web contents, social media contents, video with comments, etc.)":
                "Other",
            Multimedia: "Other",
            "Mixed material": "Other",
            "Tactile (Braille, etc.)": "Physical Object",
            Unspecified: "Other",
        },
    },
]);
