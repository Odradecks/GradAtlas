"""Target universities and master's programs for catalog coverage.

Program names follow the ingestion list. This module stores names, countries,
and field tags only. It does not store tuition, language scores, or deadlines.
"""

from __future__ import annotations


def P(slug: str, name: str, degree: str, *fields: str, department: str | None = None) -> dict:
    row = {
        "slug": slug,
        "name_en": name,
        "degree_type": degree,
        "fields": list(fields),
    }
    if department:
        row["department"] = department
    return row


def U(
    priority: str | None,
    slug: str,
    name: str,
    country: str,
    city: str,
    website: str,
    aliases: list[str],
    department: str,
    programs: list[dict],
    local: str | None = None,
) -> dict:
    return {
        "priority": priority,
        "slug": slug,
        "name_en": name,
        "name_local": local,
        "country_code": country,
        "city": city,
        "website_url": website,
        "aliases": aliases,
        "department": department,
        "programs": programs,
    }


TARGETS: list[dict] = [
    # United States
    U("P0", "stanford-university", "Stanford University", "US", "Stanford", "https://www.stanford.edu", ["Stanford"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P0", "carnegie-mellon-university", "Carnegie Mellon University", "US", "Pittsburgh", "https://www.cmu.edu", ["CMU"], "School of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
        P("ms-artificial-intelligence", "MS Artificial Intelligence", "MS", "ai"),
        P("ms-machine-learning", "MS Machine Learning", "MS", "ai"),
        P("ms-software-engineering", "MS Software Engineering", "MS", "software-engineering"),
    ]),
    U("P0", "university-of-california-berkeley", "University of California, Berkeley", "US", "Berkeley", "https://www.berkeley.edu", ["UC Berkeley", "Berkeley"], "Electrical Engineering and Computer Sciences", [
        P("meng-eecs", "MEng EECS", "MEng", "cs"),
    ]),
    U("P0", "cornell-university", "Cornell University", "US", "Ithaca", "https://www.cornell.edu", ["Cornell"], "Department of Computer Science", [
        P("meng-computer-science", "MEng Computer Science", "MEng", "cs"),
    ]),
    U("P0", "columbia-university", "Columbia University", "US", "New York", "https://www.columbia.edu", ["Columbia"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P0", "new-york-university", "New York University", "US", "New York", "https://www.nyu.edu", ["NYU"], "Courant Institute of Mathematical Sciences", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
        P("ms-data-science", "MS Data Science", "MS", "data-science", department="Center for Data Science"),
    ]),
    U("P0", "georgia-institute-of-technology", "Georgia Institute of Technology", "US", "Atlanta", "https://www.gatech.edu", ["Georgia Tech"], "College of Computing", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P0", "university-of-illinois-urbana-champaign", "University of Illinois Urbana-Champaign", "US", "Urbana-Champaign", "https://illinois.edu", ["UIUC"], "Department of Computer Science", [
        P("mscs", "MSCS", "MSCS", "cs"),
        P("mcs", "MCS", "MCS", "cs"),
    ]),
    U("P0", "university-of-texas-at-austin", "University of Texas at Austin", "US", "Austin", "https://www.utexas.edu", ["UT Austin"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P0", "university-of-california-san-diego", "University of California, San Diego", "US", "San Diego", "https://ucsd.edu", ["UCSD"], "Department of Computer Science and Engineering", [
        P("ms-computer-science-and-engineering", "MS Computer Science and Engineering", "MS", "cs"),
    ]),
    U("P1", "university-of-california-los-angeles", "University of California, Los Angeles", "US", "Los Angeles", "https://www.ucla.edu", ["UCLA"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P1", "university-of-southern-california", "University of Southern California", "US", "Los Angeles", "https://www.usc.edu", ["USC"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
        P("ms-artificial-intelligence", "MS Artificial Intelligence", "MS", "ai"),
        P("ms-data-science", "MS Data Science", "MS", "data-science"),
    ]),
    U("P1", "university-of-michigan", "University of Michigan", "US", "Ann Arbor", "https://umich.edu", ["UMich", "Michigan"], "Computer Science and Engineering", [
        P("ms-computer-science-and-engineering", "MS Computer Science and Engineering", "MS", "cs"),
    ]),
    U("P1", "university-of-pennsylvania", "University of Pennsylvania", "US", "Philadelphia", "https://www.upenn.edu", ["UPenn", "Penn"], "Department of Computer and Information Science", [
        P("mse-computer-and-information-science", "MSE Computer and Information Science", "MSE", "cs"),
    ]),
    U("P1", "princeton-university", "Princeton University", "US", "Princeton", "https://www.princeton.edu", ["Princeton"], "Department of Computer Science", [
        P("mse-computer-science", "MSE Computer Science", "MSE", "cs"),
    ]),
    U("P1", "yale-university", "Yale University", "US", "New Haven", "https://www.yale.edu", ["Yale"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P1", "brown-university", "Brown University", "US", "Providence", "https://www.brown.edu", ["Brown"], "Department of Computer Science", [
        P("scm-computer-science", "ScM Computer Science", "ScM", "cs"),
    ]),
    U("P1", "duke-university", "Duke University", "US", "Durham", "https://www.duke.edu", ["Duke"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
        P("meng-artificial-intelligence", "MEng Artificial Intelligence", "MEng", "ai"),
    ]),
    U("P1", "northwestern-university", "Northwestern University", "US", "Evanston", "https://www.northwestern.edu", ["Northwestern"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P1", "johns-hopkins-university", "Johns Hopkins University", "US", "Baltimore", "https://www.jhu.edu", ["JHU", "Johns Hopkins"], "Department of Computer Science", [
        P("mse-computer-science", "MSE Computer Science", "MSE", "cs"),
    ]),
    U("P1", "university-of-maryland-college-park", "University of Maryland, College Park", "US", "College Park", "https://www.umd.edu", ["UMD"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P1", "purdue-university", "Purdue University", "US", "West Lafayette", "https://www.purdue.edu", ["Purdue"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P1", "university-of-wisconsin-madison", "University of Wisconsin-Madison", "US", "Madison", "https://www.wisc.edu", ["UW-Madison", "Wisconsin"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
        P("professional-computer-science", "Professional Computer Science", "MS", "cs"),
    ]),
    U("P1", "university-of-massachusetts-amherst", "University of Massachusetts Amherst", "US", "Amherst", "https://www.umass.edu", ["UMass Amherst", "UMass"], "Manning College of Information and Computer Sciences", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P1", "northeastern-university", "Northeastern University", "US", "Boston", "https://www.northeastern.edu", ["Northeastern"], "Khoury College of Computer Sciences", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
        P("ms-artificial-intelligence", "MS Artificial Intelligence", "MS", "ai"),
        P("ms-data-science", "MS Data Science", "MS", "data-science"),
    ]),
    U("P1", "rice-university", "Rice University", "US", "Houston", "https://www.rice.edu", ["Rice"], "Department of Computer Science", [
        P("mcs", "MCS", "MCS", "cs"),
    ]),
    U("P1", "university-of-california-irvine", "University of California, Irvine", "US", "Irvine", "https://uci.edu", ["UC Irvine", "UCI"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
        P("mcs", "MCS", "MCS", "cs"),
    ]),
    U("P1", "university-of-california-davis", "University of California, Davis", "US", "Davis", "https://www.ucdavis.edu", ["UC Davis"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P2", "rutgers-university", "Rutgers University", "US", "New Brunswick", "https://www.rutgers.edu", ["Rutgers"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P2", "stony-brook-university", "Stony Brook University", "US", "Stony Brook", "https://www.stonybrook.edu", ["Stony Brook", "SBU"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P2", "virginia-tech", "Virginia Tech", "US", "Blacksburg", "https://vt.edu", ["Virginia Tech", "VT"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P2", "texas-a-and-m-university", "Texas A&M University", "US", "College Station", "https://www.tamu.edu", ["Texas A&M", "TAMU"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P2", "university-of-minnesota", "University of Minnesota", "US", "Minneapolis", "https://twin-cities.umn.edu", ["UMN"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U("P2", "ohio-state-university", "Ohio State University", "US", "Columbus", "https://www.osu.edu", ["Ohio State", "OSU"], "Department of Computer Science and Engineering", [
        P("ms-computer-science-and-engineering", "MS Computer Science and Engineering", "MS", "cs"),
    ]),
    U("P2", "pennsylvania-state-university", "Pennsylvania State University", "US", "University Park", "https://www.psu.edu", ["Penn State"], "Department of Computer Science and Engineering", [
        P("ms-computer-science-and-engineering", "MS Computer Science and Engineering", "MS", "cs"),
    ]),
    U("P2", "university-of-colorado-boulder", "University of Colorado Boulder", "US", "Boulder", "https://www.colorado.edu", ["CU Boulder"], "Department of Computer Science", [
        P("ms-computer-science", "MS Computer Science", "MS", "cs"),
    ]),
    U(None, "massachusetts-institute-of-technology", "Massachusetts Institute of Technology", "US", "Cambridge", "https://www.mit.edu", ["MIT"], "Electrical Engineering and Computer Science", []),
    # Canada
    U("P0", "university-of-toronto", "University of Toronto", "CA", "Toronto", "https://www.utoronto.ca", ["U of T", "Toronto"], "Department of Computer Science", [
        P("mscac-computer-science", "MScAC Computer Science", "MScAC", "cs"),
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U("P0", "university-of-british-columbia", "University of British Columbia", "CA", "Vancouver", "https://www.ubc.ca", ["UBC"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("master-of-data-science", "Master of Data Science", "Master", "data-science"),
    ]),
    U("P0", "university-of-waterloo", "University of Waterloo", "CA", "Waterloo", "https://uwaterloo.ca", ["Waterloo"], "David R. Cheriton School of Computer Science", [
        P("mmath-computer-science", "MMath Computer Science", "MMath", "cs"),
        P("data-science", "Data Science", "Master", "data-science"),
    ]),
    U("P0", "mcgill-university", "McGill University", "CA", "Montreal", "https://www.mcgill.ca", ["McGill"], "School of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U("P1", "university-of-alberta", "University of Alberta", "CA", "Edmonton", "https://www.ualberta.ca", ["UAlberta"], "Department of Computing Science", [
        P("msc-computing-science", "MSc Computing Science", "MSc", "cs"),
    ]),
    U("P1", "simon-fraser-university", "Simon Fraser University", "CA", "Burnaby", "https://www.sfu.ca", ["SFU"], "School of Computing Science", [
        P("msc-computing-science", "MSc Computing Science", "MSc", "cs"),
        P("professional-computer-science", "Professional Computer Science", "Master", "cs"),
    ]),
    U("P1", "mcmaster-university", "McMaster University", "CA", "Hamilton", "https://www.mcmaster.ca", ["McMaster"], "Department of Computing and Software", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U("P1", "queens-university", "Queen's University", "CA", "Kingston", "https://www.queensu.ca", ["Queen's"], "School of Computing", [
        P("msc-computing", "MSc Computing", "MSc", "cs"),
    ]),
    U("P1", "university-of-ottawa", "University of Ottawa", "CA", "Ottawa", "https://www.uottawa.ca", ["uOttawa"], "School of Electrical Engineering and Computer Science", [
        P("master-of-computer-science", "Master of Computer Science", "Master", "cs"),
    ]),
    U("P1", "carleton-university", "Carleton University", "CA", "Ottawa", "https://carleton.ca", ["Carleton"], "School of Computer Science", [
        P("master-of-computer-science", "Master of Computer Science", "Master", "cs"),
    ]),
    U("P2", "western-university", "Western University", "CA", "London", "https://www.uwo.ca", ["Western", "UWO"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U("P2", "concordia-university", "Concordia University", "CA", "Montreal", "https://www.concordia.ca", ["Concordia"], "Department of Computer Science and Software Engineering", [
        P("mcompsc", "MCompSc", "MCompSc", "cs"),
    ]),
    U("P2", "dalhousie-university", "Dalhousie University", "CA", "Halifax", "https://www.dal.ca", ["Dalhousie"], "Faculty of Computer Science", [
        P("master-of-applied-computer-science", "Master of Applied Computer Science", "Master", "cs"),
    ]),
    U("P2", "university-of-calgary", "University of Calgary", "CA", "Calgary", "https://www.ucalgary.ca", ["UCalgary"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U("P2", "university-of-victoria", "University of Victoria", "CA", "Victoria", "https://www.uvic.ca", ["UVic"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    # United Kingdom
    U("P0", "university-of-oxford", "University of Oxford", "GB", "Oxford", "https://www.ox.ac.uk", ["Oxford"], "Department of Computer Science", [
        P("msc-advanced-computer-science", "MSc Advanced Computer Science", "MSc", "cs"),
    ]),
    U("P0", "university-of-cambridge", "University of Cambridge", "GB", "Cambridge", "https://www.cam.ac.uk", ["Cambridge"], "Department of Computer Science and Technology", [
        P("mphil-advanced-computer-science", "MPhil Advanced Computer Science", "MPhil", "cs"),
    ]),
    U("P0", "imperial-college-london", "Imperial College London", "GB", "London", "https://www.imperial.ac.uk", ["Imperial"], "Department of Computing", [
        P("msc-computing", "MSc Computing", "MSc", "cs"),
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
        P("msc-advanced-computing", "MSc Advanced Computing", "MSc", "cs"),
    ]),
    U("P0", "university-college-london", "University College London", "GB", "London", "https://www.ucl.ac.uk", ["UCL"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-machine-learning", "MSc Machine Learning", "MSc", "ai"),
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
    ]),
    U("P0", "university-of-edinburgh", "University of Edinburgh", "GB", "Edinburgh", "https://www.ed.ac.uk", ["Edinburgh"], "School of Informatics", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
        P("msc-informatics", "MSc Informatics", "MSc", "cs"),
    ]),
    U("P0", "university-of-manchester", "University of Manchester", "GB", "Manchester", "https://www.manchester.ac.uk", ["Manchester"], "Department of Computer Science", [
        P("msc-advanced-computer-science", "MSc Advanced Computer Science", "MSc", "cs"),
    ]),
    U("P0", "kings-college-london", "King's College London", "GB", "London", "https://www.kcl.ac.uk", ["King's", "KCL"], "Department of Informatics", [
        P("msc-advanced-computing", "MSc Advanced Computing", "MSc", "cs"),
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
    ]),
    U("P1", "university-of-warwick", "University of Warwick", "GB", "Coventry", "https://warwick.ac.uk", ["Warwick"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-data-analytics", "MSc Data Analytics", "MSc", "data-science"),
    ]),
    U("P1", "university-of-bristol", "University of Bristol", "GB", "Bristol", "https://www.bristol.ac.uk", ["Bristol"], "School of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U("P1", "university-of-southampton", "University of Southampton", "GB", "Southampton", "https://www.southampton.ac.uk", ["Southampton"], "School of Electronics and Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
    ]),
    U("P1", "university-of-birmingham", "University of Birmingham", "GB", "Birmingham", "https://www.birmingham.ac.uk", ["Birmingham"], "School of Computer Science", [
        P("msc-advanced-computer-science", "MSc Advanced Computer Science", "MSc", "cs"),
    ]),
    U("P1", "university-of-glasgow", "University of Glasgow", "GB", "Glasgow", "https://www.gla.ac.uk", ["Glasgow"], "School of Computing Science", [
        P("msc-computing-science", "MSc Computing Science", "MSc", "cs"),
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
    ]),
    U("P1", "university-of-sheffield", "University of Sheffield", "GB", "Sheffield", "https://www.sheffield.ac.uk", ["Sheffield"], "School of Computer Science", [
        P("msc-advanced-computer-science", "MSc Advanced Computer Science", "MSc", "cs"),
    ]),
    U("P1", "university-of-leeds", "University of Leeds", "GB", "Leeds", "https://www.leeds.ac.uk", ["Leeds"], "School of Computer Science", [
        P("msc-advanced-computer-science", "MSc Advanced Computer Science", "MSc", "cs"),
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
    ]),
    U("P1", "university-of-nottingham", "University of Nottingham", "GB", "Nottingham", "https://www.nottingham.ac.uk", ["Nottingham"], "School of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U("P1", "durham-university", "Durham University", "GB", "Durham", "https://www.durham.ac.uk", ["Durham"], "Department of Computer Science", [
        P("msc-advanced-computer-science", "MSc Advanced Computer Science", "MSc", "cs"),
    ]),
    U("P1", "university-of-st-andrews", "University of St Andrews", "GB", "St Andrews", "https://www.st-andrews.ac.uk", ["St Andrews"], "School of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
    ]),
    U("P2", "university-of-bath", "University of Bath", "GB", "Bath", "https://www.bath.ac.uk", ["Bath"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
    ]),
    U("P2", "queen-mary-university-of-london", "Queen Mary University of London", "GB", "London", "https://www.qmul.ac.uk", ["QMUL", "Queen Mary"], "School of Electronic Engineering and Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
    ]),
    U("P2", "lancaster-university", "Lancaster University", "GB", "Lancaster", "https://www.lancaster.ac.uk", ["Lancaster"], "School of Computing and Communications", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    # Ireland
    U(None, "trinity-college-dublin", "Trinity College Dublin", "IE", "Dublin", "https://www.tcd.ie", ["TCD", "Trinity"], "School of Computer Science and Statistics", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U(None, "university-college-dublin", "University College Dublin", "IE", "Dublin", "https://www.ucd.ie", ["UCD"], "School of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-data-and-computational-science", "MSc Data and Computational Science", "MSc", "data-science"),
    ]),
    U(None, "dublin-city-university", "Dublin City University", "IE", "Dublin", "https://www.dcu.ie", ["DCU"], "School of Computing", [
        P("msc-computing", "MSc Computing", "MSc", "cs"),
    ]),
    U(None, "university-of-galway", "University of Galway", "IE", "Galway", "https://www.universityofgalway.ie", ["Galway"], "School of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U(None, "university-college-cork", "University College Cork", "IE", "Cork", "https://www.ucc.ie", ["UCC"], "School of Computer Science and Information Technology", [
        P("msc-computing-science", "MSc Computing Science", "MSc", "cs"),
    ]),
    U(None, "university-of-limerick", "University of Limerick", "IE", "Limerick", "https://www.ul.ie", ["UL"], "Department of Computer Science and Information Systems", [
        P("msc-software-engineering", "MSc Software Engineering", "MSc", "software-engineering"),
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
    ]),
    # Germany
    U("P0", "technical-university-of-munich", "Technical University of Munich", "DE", "Munich", "https://www.tum.de", ["TUM", "TU München"], "Department of Informatics", [
        P("msc-informatics", "MSc Informatics", "MSc", "cs"),
        P("msc-data-engineering-and-analytics", "MSc Data Engineering and Analytics", "MSc", "data-science", department="School of Computation, Information and Technology"),
    ], local="Technische Universität München"),
    U("P0", "rwth-aachen-university", "RWTH Aachen University", "DE", "Aachen", "https://www.rwth-aachen.de", ["RWTH", "RWTH Aachen"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
    ]),
    U("P0", "karlsruhe-institute-of-technology", "Karlsruhe Institute of Technology", "DE", "Karlsruhe", "https://www.kit.edu", ["KIT"], "Department of Informatics", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Karlsruher Institut für Technologie"),
    U("P0", "saarland-university", "Saarland University", "DE", "Saarbrücken", "https://www.uni-saarland.de", ["Saarland"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-data-science-and-ai", "MSc Data Science and AI", "MSc", "data-science", "ai"),
    ], local="Universität des Saarlandes"),
    U("P0", "tu-berlin", "TU Berlin", "DE", "Berlin", "https://www.tu.berlin", ["TU Berlin", "Technische Universität Berlin"], "Faculty of Electrical Engineering and Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Technische Universität Berlin"),
    U("P0", "tu-darmstadt", "TU Darmstadt", "DE", "Darmstadt", "https://www.tu-darmstadt.de", ["TU Darmstadt"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-ai-and-machine-learning", "MSc AI and Machine Learning", "MSc", "ai"),
    ], local="Technische Universität Darmstadt"),
    U("P1", "lmu-munich", "LMU Munich", "DE", "Munich", "https://www.lmu.de", ["LMU"], "Institute of Informatics", [
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
    ], local="Ludwig-Maximilians-Universität München"),
    U("P1", "university-of-freiburg", "University of Freiburg", "DE", "Freiburg", "https://uni-freiburg.de", ["Freiburg"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Albert-Ludwigs-Universität Freiburg"),
    U("P1", "university-of-bonn", "University of Bonn", "DE", "Bonn", "https://www.uni-bonn.de", ["Bonn"], "Institute of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Rheinische Friedrich-Wilhelms-Universität Bonn"),
    U("P1", "heidelberg-university", "Heidelberg University", "DE", "Heidelberg", "https://www.uni-heidelberg.de", ["Heidelberg"], "Department of Mathematics and Computer Science", [
        P("msc-data-and-computer-science", "MSc Data and Computer Science", "MSc", "cs", "data-science"),
    ], local="Universität Heidelberg"),
    U("P1", "university-of-stuttgart", "University of Stuttgart", "DE", "Stuttgart", "https://www.uni-stuttgart.de", ["Stuttgart"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Universität Stuttgart"),
    U("P1", "fau-erlangen-nurnberg", "FAU Erlangen-Nürnberg", "DE", "Erlangen", "https://www.fau.de", ["FAU"], "Department of Computer Science", [
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
    ], local="Friedrich-Alexander-Universität Erlangen-Nürnberg"),
    U("P1", "tu-dresden", "TU Dresden", "DE", "Dresden", "https://tu-dresden.de", ["TU Dresden"], "Faculty of Computer Science", [
        P("msc-computer-science-distributed-systems", "MSc Computer Science / Distributed Systems", "MSc", "cs"),
    ], local="Technische Universität Dresden"),
    U("P1", "university-of-hamburg", "University of Hamburg", "DE", "Hamburg", "https://www.uni-hamburg.de", ["Hamburg"], "Department of Informatics", [
        P("msc-informatics", "MSc Informatics", "MSc", "cs"),
    ], local="Universität Hamburg"),
    U("P2", "university-of-tubingen", "University of Tübingen", "DE", "Tübingen", "https://uni-tuebingen.de", ["Tübingen"], "Department of Computer Science", [
        P("msc-machine-learning", "MSc Machine Learning", "MSc", "ai"),
    ], local="Eberhard Karls Universität Tübingen"),
    U("P2", "university-of-mannheim", "University of Mannheim", "DE", "Mannheim", "https://www.uni-mannheim.de", ["Mannheim"], "School of Business Informatics and Mathematics", [
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
    ], local="Universität Mannheim"),
    U("P2", "university-of-potsdam", "University of Potsdam", "DE", "Potsdam", "https://www.uni-potsdam.de", ["Potsdam"], "Institute of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Universität Potsdam"),
    U("P2", "university-of-passau", "University of Passau", "DE", "Passau", "https://www.uni-passau.de", ["Passau"], "Faculty of Computer Science and Mathematics", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Universität Passau"),
    # Netherlands
    U("P0", "delft-university-of-technology", "Delft University of Technology", "NL", "Delft", "https://www.tudelft.nl", ["TU Delft", "Delft"], "Faculty of Electrical Engineering, Mathematics and Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U("P0", "eindhoven-university-of-technology", "Eindhoven University of Technology", "NL", "Eindhoven", "https://www.tue.nl", ["TU/e", "Eindhoven"], "Department of Mathematics and Computer Science", [
        P("msc-computer-science-and-engineering", "MSc Computer Science and Engineering", "MSc", "cs"),
    ]),
    U("P0", "university-of-amsterdam", "University of Amsterdam", "NL", "Amsterdam", "https://www.uva.nl", ["UvA"], "Informatics Institute", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
    ]),
    U("P0", "vrije-universiteit-amsterdam", "Vrije Universiteit Amsterdam", "NL", "Amsterdam", "https://vu.nl", ["VU Amsterdam", "VU"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
    ]),
    U("P1", "utrecht-university", "Utrecht University", "NL", "Utrecht", "https://www.uu.nl", ["Utrecht"], "Department of Information and Computing Sciences", [
        P("msc-computing-science", "MSc Computing Science", "MSc", "cs"),
    ]),
    U("P1", "leiden-university", "Leiden University", "NL", "Leiden", "https://www.universiteitleiden.nl", ["Leiden"], "Leiden Institute of Advanced Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U("P1", "university-of-groningen", "University of Groningen", "NL", "Groningen", "https://www.rug.nl", ["Groningen", "RUG"], "Bernoulli Institute", [
        P("msc-computing-science", "MSc Computing Science", "MSc", "cs"),
    ]),
    U("P1", "university-of-twente", "University of Twente", "NL", "Enschede", "https://www.utwente.nl", ["Twente", "UT"], "Faculty of Electrical Engineering, Mathematics and Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U("P1", "radboud-university", "Radboud University", "NL", "Nijmegen", "https://www.ru.nl", ["Radboud"], "Institute for Computing and Information Sciences", [
        P("msc-computing-science", "MSc Computing Science", "MSc", "cs"),
    ]),
    U("P1", "maastricht-university", "Maastricht University", "NL", "Maastricht", "https://www.maastrichtuniversity.nl", ["Maastricht", "UM"], "Department of Advanced Computing Sciences", [
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
    ]),
    # Belgium
    U(None, "ku-leuven", "KU Leuven", "BE", "Leuven", "https://www.kuleuven.be", ["KU Leuven"], "Department of Computer Science", [
        P("master-of-computer-science", "Master of Computer Science", "Master", "cs"),
    ]),
    U(None, "ghent-university", "Ghent University", "BE", "Ghent", "https://www.ugent.be", ["UGent", "Ghent"], "Faculty of Engineering and Architecture", [
        P("msc-computer-science-engineering", "MSc Computer Science Engineering", "MSc", "cs"),
    ], local="Universiteit Gent"),
    U(None, "uclouvain", "UCLouvain", "BE", "Louvain-la-Neuve", "https://uclouvain.be", ["UCLouvain"], "Ecole Polytechnique de Louvain", [
        P("master-computer-science", "Master Computer Science", "Master", "cs"),
    ]),
    U(None, "university-of-antwerp", "University of Antwerp", "BE", "Antwerp", "https://www.uantwerpen.be", ["UAntwerp"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Universiteit Antwerpen"),
    U(None, "vrije-universiteit-brussel", "Vrije Universiteit Brussel", "BE", "Brussels", "https://www.vub.be", ["VUB"], "Department of Computer Science", [
        P("msc-applied-computer-science", "MSc Applied Computer Science", "MSc", "cs"),
    ]),
    # Switzerland
    U("P0", "eth-zurich", "ETH Zürich", "CH", "Zürich", "https://ethz.ch", ["ETH", "ETH Zurich"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
    ]),
    U("P0", "epfl", "EPFL", "CH", "Lausanne", "https://www.epfl.ch", ["EPFL"], "School of Computer and Communication Sciences", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
    ]),
    U("P1", "university-of-zurich", "University of Zurich", "CH", "Zürich", "https://www.uzh.ch", ["UZH"], "Department of Informatics", [
        P("msc-informatics", "MSc Informatics", "MSc", "cs"),
    ], local="Universität Zürich"),
    U("P1", "university-of-basel", "University of Basel", "CH", "Basel", "https://www.unibas.ch", ["Basel"], "Department of Mathematics and Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Universität Basel"),
    U("P1", "university-of-bern", "University of Bern", "CH", "Bern", "https://www.unibe.ch", ["Bern"], "Institute of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Universität Bern"),
    # Austria
    U(None, "tu-wien", "TU Wien", "AT", "Vienna", "https://www.tuwien.at", ["TU Wien"], "Faculty of Informatics", [
        P("msc-logic-and-computation", "MSc Logic and Computation", "MSc", "cs"),
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
        P("msc-computer-engineering", "MSc Computer Engineering", "MSc", "cs"),
    ], local="Technische Universität Wien"),
    U(None, "johannes-kepler-university-linz", "Johannes Kepler University Linz", "AT", "Linz", "https://www.jku.at", ["JKU", "JKU Linz"], "Institute of Computer Science", [
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U(None, "tu-graz", "TU Graz", "AT", "Graz", "https://www.tugraz.at", ["TU Graz"], "Faculty of Computer Science and Biomedical Engineering", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
    ], local="Technische Universität Graz"),
    U(None, "university-of-vienna", "University of Vienna", "AT", "Vienna", "https://www.univie.ac.at", ["Vienna"], "Faculty of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Universität Wien"),
    U(None, "university-of-innsbruck", "University of Innsbruck", "AT", "Innsbruck", "https://www.uibk.ac.at", ["Innsbruck"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Universität Innsbruck"),
    # France
    U(None, "universite-paris-saclay", "Université Paris-Saclay", "FR", "Gif-sur-Yvette", "https://www.universite-paris-saclay.fr", ["Paris-Saclay"], "Graduate School of Computer Science", [
        P("master-informatique", "Master Informatique", "Master", "cs"),
        P("master-artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
        P("master-data-science", "Data Science", "Master", "data-science"),
    ]),
    U(None, "institut-polytechnique-de-paris", "Institut Polytechnique de Paris", "FR", "Palaiseau", "https://www.ip-paris.fr", ["IP Paris"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
        P("data-science", "Data Science", "Master", "data-science"),
    ]),
    U(None, "sorbonne-universite", "Sorbonne Université", "FR", "Paris", "https://www.sorbonne-universite.fr", ["Sorbonne"], "Faculté des Sciences et Ingénierie", [
        P("master-informatique", "Master Informatique", "Master", "cs"),
    ]),
    U(None, "universite-psl", "Université PSL", "FR", "Paris", "https://psl.eu", ["PSL"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("data-science", "Data Science", "Master", "data-science"),
    ]),
    U(None, "ecole-polytechnique", "École Polytechnique", "FR", "Palaiseau", "https://www.polytechnique.edu", ["École Polytechnique", "l'X"], "Computer Science", [
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
        P("data-science", "Data Science", "Master", "data-science"),
        P("computer-science", "Computer Science", "Master", "cs"),
    ]),
    U(None, "ens-paris-saclay", "ENS Paris-Saclay", "FR", "Gif-sur-Yvette", "https://ens-paris-saclay.fr", ["ENS Paris-Saclay"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
    ]),
    U(None, "universite-grenoble-alpes", "Université Grenoble Alpes", "FR", "Grenoble", "https://www.univ-grenoble-alpes.fr", ["UGA"], "Computer Science", [
        P("mosig", "MoSIG", "Master", "cs"),
        P("computer-science", "Computer Science", "Master", "cs"),
    ]),
    U(None, "universite-paris-cite", "Université Paris Cité", "FR", "Paris", "https://u-paris.fr", ["Paris Cité"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("data-science", "Data Science", "Master", "data-science"),
    ]),
    U(None, "universite-cote-dazur", "Université Côte d'Azur", "FR", "Nice", "https://univ-cotedazur.fr", ["UCA"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
    ]),
    U(None, "universite-de-rennes", "Université de Rennes", "FR", "Rennes", "https://www.univ-rennes.fr", ["Rennes"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
    ]),
    U(None, "universite-de-bordeaux", "Université de Bordeaux", "FR", "Bordeaux", "https://www.u-bordeaux.fr", ["Bordeaux"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
    ]),
    U(None, "universite-de-lille", "Université de Lille", "FR", "Lille", "https://www.univ-lille.fr", ["Lille"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
    ]),
    U(None, "universite-de-strasbourg", "Université de Strasbourg", "FR", "Strasbourg", "https://www.unistra.fr", ["Strasbourg"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
    ]),
    U(None, "universite-de-lyon", "Université de Lyon", "FR", "Lyon", "https://www.universite-lyon.fr", ["Lyon"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
    ]),
    U(None, "ens-lyon", "ENS Lyon", "FR", "Lyon", "https://www.ens-lyon.fr", ["ENS de Lyon"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
    ]),
    U(None, "universite-de-toulouse", "Université de Toulouse", "FR", "Toulouse", "https://www.univ-toulouse.fr", ["Toulouse"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
    ]),
    # Sweden
    U(None, "kth-royal-institute-of-technology", "KTH Royal Institute of Technology", "SE", "Stockholm", "https://www.kth.se", ["KTH"], "School of Electrical Engineering and Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-machine-learning", "MSc Machine Learning", "MSc", "ai"),
    ]),
    U(None, "chalmers-university-of-technology", "Chalmers University of Technology", "SE", "Gothenburg", "https://www.chalmers.se", ["Chalmers"], "Department of Computer Science and Engineering", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
    ]),
    U(None, "lund-university", "Lund University", "SE", "Lund", "https://www.lu.se", ["Lund"], "Department of Computer Science", [
        P("msc-machine-learning", "MSc Machine Learning", "MSc", "ai"),
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U(None, "uppsala-university", "Uppsala University", "SE", "Uppsala", "https://www.uu.se", ["Uppsala"], "Department of Information Technology", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U(None, "stockholm-university", "Stockholm University", "SE", "Stockholm", "https://www.su.se", ["Stockholm"], "Department of Computer and Systems Sciences", [
        P("msc-computer-and-systems-sciences", "MSc Computer and Systems Sciences", "MSc", "cs"),
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
    ]),
    U(None, "linkoping-university", "Linköping University", "SE", "Linköping", "https://liu.se", ["LiU", "Linköping"], "Department of Computer and Information Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U(None, "university-of-gothenburg", "University of Gothenburg", "SE", "Gothenburg", "https://www.gu.se", ["Gothenburg"], "Department of Computer Science and Engineering", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U(None, "umea-university", "Umeå University", "SE", "Umeå", "https://www.umu.se", ["Umeå"], "Department of Computing Science", [
        P("msc-computing-science", "MSc Computing Science", "MSc", "cs"),
    ]),
    # Finland
    U(None, "aalto-university", "Aalto University", "FI", "Espoo", "https://www.aalto.fi", ["Aalto"], "School of Science", [
        P("msc-computer-communication-and-information-sciences", "MSc Computer, Communication and Information Sciences", "MSc", "cs"),
    ]),
    U(None, "university-of-helsinki", "University of Helsinki", "FI", "Helsinki", "https://www.helsinki.fi", ["UH", "Helsinki"], "Department of Computer Science", [
        P("msc-computer-science", "Master's Programme in Computer Science", "MSc", "cs"),
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
    ], local="Helsingin yliopisto"),
    U(None, "tampere-university", "Tampere University", "FI", "Tampere", "https://www.tuni.fi", ["Tampere"], "Faculty of Information Technology and Communication Sciences", [
        P("msc-computing-sciences", "MSc Computing Sciences", "MSc", "cs"),
    ]),
    U(None, "university-of-turku", "University of Turku", "FI", "Turku", "https://www.utu.fi", ["Turku"], "Department of Computing", [
        P("msc-ict", "MSc ICT", "MSc", "cs"),
    ]),
    U(None, "university-of-oulu", "University of Oulu", "FI", "Oulu", "https://www.oulu.fi", ["Oulu"], "Faculty of Information Technology and Electrical Engineering", [
        P("msc-computer-science-and-engineering", "MSc Computer Science and Engineering", "MSc", "cs"),
    ]),
    # Denmark
    U(None, "technical-university-of-denmark", "Technical University of Denmark", "DK", "Kongens Lyngby", "https://www.dtu.dk", ["DTU"], "Department of Applied Mathematics and Computer Science", [
        P("msc-computer-science-and-engineering", "MSc Computer Science and Engineering", "MSc", "cs"),
    ]),
    U(None, "university-of-copenhagen", "University of Copenhagen", "DK", "Copenhagen", "https://www.ku.dk", ["UCPH", "KU"], "Department of Computer Science", [
        P("msc-computer-science", "MSc in Computer Science", "MSc", "cs"),
    ], local="Københavns Universitet"),
    U(None, "aarhus-university", "Aarhus University", "DK", "Aarhus", "https://www.au.dk", ["Aarhus", "AU"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U(None, "aalborg-university", "Aalborg University", "DK", "Aalborg", "https://www.aau.dk", ["Aalborg", "AAU"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    # Norway
    U(None, "ntnu", "NTNU", "NO", "Trondheim", "https://www.ntnu.edu", ["NTNU", "Norwegian University of Science and Technology"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-informatics", "MSc Informatics", "MSc", "cs"),
    ], local="Norges teknisk-naturvitenskapelige universitet"),
    U(None, "university-of-oslo", "University of Oslo", "NO", "Oslo", "https://www.uio.no", ["UiO"], "Department of Informatics", [
        P("msc-informatics", "MSc Informatics", "MSc", "cs"),
    ], local="Universitetet i Oslo"),
    U(None, "university-of-bergen", "University of Bergen", "NO", "Bergen", "https://www.uib.no", ["UiB"], "Department of Informatics", [
        P("msc-informatics", "MSc Informatics", "MSc", "cs"),
    ], local="Universitetet i Bergen"),
    U(None, "university-of-stavanger", "University of Stavanger", "NO", "Stavanger", "https://www.uis.no", ["UiS"], "Department of Electrical Engineering and Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
    ], local="Universitetet i Stavanger"),
    # Spain
    U(None, "universitat-politecnica-de-catalunya", "Universitat Politècnica de Catalunya", "ES", "Barcelona", "https://www.upc.edu", ["UPC", "BarcelonaTech"], "Computer Science", [
        P("master-in-innovation-and-research-in-informatics", "Master in Innovation and Research in Informatics", "Master", "cs"),
    ]),
    U(None, "universidad-politecnica-de-madrid", "Universidad Politécnica de Madrid", "ES", "Madrid", "https://www.upm.es", ["UPM"], "Computer Science", [
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U(None, "universidad-carlos-iii-de-madrid", "Universidad Carlos III de Madrid", "ES", "Madrid", "https://www.uc3m.es", ["UC3M"], "Department of Computer Science", [
        P("msc-computer-science-and-technology", "MSc Computer Science and Technology", "MSc", "cs"),
    ]),
    U(None, "universidad-autonoma-de-madrid", "Universidad Autónoma de Madrid", "ES", "Madrid", "https://www.uam.es", ["UAM"], "Computer Science", [
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
        P("data-science", "Data Science", "Master", "data-science"),
    ]),
    U(None, "universidad-complutense-de-madrid", "Universidad Complutense de Madrid", "ES", "Madrid", "https://www.ucm.es", ["UCM"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
    ]),
    U(None, "university-of-barcelona", "University of Barcelona", "ES", "Barcelona", "https://www.ub.edu", ["UB"], "Computer Science", [
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
        P("data-science", "Data Science", "Master", "data-science"),
    ], local="Universitat de Barcelona"),
    U(None, "pompeu-fabra-university", "Pompeu Fabra University", "ES", "Barcelona", "https://www.upf.edu", ["UPF"], "Department of Engineering", [
        P("intelligent-interactive-systems", "Intelligent Interactive Systems", "Master", "ai"),
        P("data-science", "Data Science", "Master", "data-science"),
    ]),
    U(None, "universitat-politecnica-de-valencia", "Universitat Politècnica de València", "ES", "Valencia", "https://www.upv.es", ["UPV"], "Computer Engineering", [
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
        P("computer-engineering", "Computer Engineering", "Master", "cs"),
    ]),
    U(None, "autonomous-university-of-barcelona", "Autonomous University of Barcelona", "ES", "Barcelona", "https://www.uab.cat", ["UAB"], "Computer Science", [
        P("computer-vision", "Computer Vision", "Master", "ai"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
        P("data-science", "Data Science", "Master", "data-science"),
    ], local="Universitat Autònoma de Barcelona"),
    U(None, "university-of-granada", "University of Granada", "ES", "Granada", "https://www.ugr.es", ["UGR"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
    ], local="Universidad de Granada"),
    # Italy
    U(None, "politecnico-di-milano", "Politecnico di Milano", "IT", "Milan", "https://www.polimi.it", ["Polimi"], "Computer Science and Engineering", [
        P("msc-computer-science-and-engineering", "MSc Computer Science and Engineering", "MSc", "cs"),
    ]),
    U(None, "politecnico-di-torino", "Politecnico di Torino", "IT", "Turin", "https://www.polito.it", ["Polito"], "Computer Engineering", [
        P("msc-computer-engineering", "MSc Computer Engineering", "MSc", "cs"),
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
    ]),
    U(None, "sapienza-university-of-rome", "Sapienza University of Rome", "IT", "Rome", "https://www.uniroma1.it", ["Sapienza"], "Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-artificial-intelligence-and-robotics", "MSc Artificial Intelligence and Robotics", "MSc", "ai"),
    ]),
    U(None, "university-of-bologna", "University of Bologna", "IT", "Bologna", "https://www.unibo.it", ["Bologna", "UniBo"], "Computer Science", [
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
    ]),
    U(None, "university-of-padua", "University of Padua", "IT", "Padua", "https://www.unipd.it", ["Padua", "UniPd"], "Department of Mathematics", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U(None, "university-of-pisa", "University of Pisa", "IT", "Pisa", "https://www.unipi.it", ["Pisa", "UniPi"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U(None, "university-of-trento", "University of Trento", "IT", "Trento", "https://www.unitn.it", ["Trento", "UniTn"], "Department of Information Engineering and Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U(None, "university-of-milan", "University of Milan", "IT", "Milan", "https://www.unimi.it", ["UniMi"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Università degli Studi di Milano"),
    U(None, "university-of-turin", "University of Turin", "IT", "Turin", "https://www.unito.it", ["UniTo"], "Department of Computer Science", [
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="Università degli Studi di Torino"),
    U(None, "university-of-rome-tor-vergata", "University of Rome Tor Vergata", "IT", "Rome", "https://web.uniroma2.it", ["Tor Vergata"], "Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("ict", "ICT", "Master", "cs"),
    ]),
    U(None, "university-of-pavia", "University of Pavia", "IT", "Pavia", "https://web.unipv.it", ["Pavia"], "Computer Engineering", [
        P("computer-engineering", "Computer Engineering", "Master", "cs"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
    ]),
    U(None, "university-of-naples-federico-ii", "University of Naples Federico II", "IT", "Naples", "https://www.unina.it", ["Federico II"], "Department of Electrical Engineering and Information Technology", [
        P("computer-science", "Computer Science", "Master", "cs"),
    ]),
    # Portugal
    U(None, "university-of-lisbon", "University of Lisbon", "PT", "Lisbon", "https://www.ulisboa.pt", ["ULisboa", "Instituto Superior Técnico", "IST"], "Instituto Superior Técnico", [
        P("msc-computer-science-and-engineering", "MSc Computer Science and Engineering", "MSc", "cs"),
    ], local="Universidade de Lisboa"),
    U(None, "university-of-porto", "University of Porto", "PT", "Porto", "https://www.up.pt", ["UPorto"], "Faculty of Engineering", [
        P("msc-informatics-and-computing-engineering", "MSc Informatics and Computing Engineering", "MSc", "cs"),
    ], local="Universidade do Porto"),
    U(None, "nova-university-lisbon", "NOVA University Lisbon", "PT", "Lisbon", "https://www.unl.pt", ["NOVA"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ]),
    U(None, "university-of-minho", "University of Minho", "PT", "Braga", "https://www.uminho.pt", ["UMinho"], "Department of Informatics", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("msc-software-engineering", "MSc Software Engineering", "MSc", "software-engineering"),
    ], local="Universidade do Minho"),
    U(None, "university-of-coimbra", "University of Coimbra", "PT", "Coimbra", "https://www.uc.pt", ["Coimbra"], "Department of Informatics Engineering", [
        P("msc-informatics-engineering", "MSc Informatics Engineering", "MSc", "cs"),
    ], local="Universidade de Coimbra"),
    # Luxembourg
    U(None, "university-of-luxembourg", "University of Luxembourg", "LU", "Esch-sur-Alzette", "https://www.uni.lu", ["Uni.lu"], "Department of Computer Science", [
        P("master-in-information-and-computer-sciences", "Master in Information and Computer Sciences", "Master", "cs"),
        P("master-in-data-science", "Data Science", "Master", "data-science"),
    ]),
    # Australia
    U("P0", "university-of-melbourne", "University of Melbourne", "AU", "Melbourne", "https://www.unimelb.edu.au", ["Melbourne", "UniMelb"], "School of Computing and Information Systems", [
        P("master-of-computer-science", "Master of Computer Science", "Master", "cs"),
    ]),
    U("P0", "australian-national-university", "Australian National University", "AU", "Canberra", "https://www.anu.edu.au", ["ANU"], "School of Computing", [
        P("master-of-computing", "Master of Computing", "Master", "cs"),
    ]),
    U("P0", "unsw-sydney", "UNSW Sydney", "AU", "Sydney", "https://www.unsw.edu.au", ["UNSW"], "School of Computer Science and Engineering", [
        P("master-of-information-technology", "Master of Information Technology", "Master", "information-technology"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
    ]),
    U("P0", "university-of-sydney", "University of Sydney", "AU", "Sydney", "https://www.sydney.edu.au", ["USYD", "Sydney"], "School of Computer Science", [
        P("master-of-computer-science", "Master of Computer Science", "Master", "cs"),
    ]),
    U("P0", "monash-university", "Monash University", "AU", "Melbourne", "https://www.monash.edu", ["Monash"], "Faculty of Information Technology", [
        P("master-of-information-technology", "Master of Information Technology", "Master", "information-technology"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
    ]),
    U("P0", "university-of-queensland", "University of Queensland", "AU", "Brisbane", "https://www.uq.edu.au", ["UQ"], "School of Electrical Engineering and Computer Science", [
        P("master-of-information-technology", "Master of Information Technology", "Master", "information-technology"),
        P("data-science", "Data Science", "Master", "data-science"),
    ]),
    U("P1", "university-of-adelaide", "University of Adelaide", "AU", "Adelaide", "https://www.adelaide.edu.au", ["Adelaide"], "School of Computer and Mathematical Sciences", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
    ]),
    U("P1", "university-of-technology-sydney", "University of Technology Sydney", "AU", "Sydney", "https://www.uts.edu.au", ["UTS"], "Faculty of Engineering and Information Technology", [
        P("master-of-information-technology", "Master of Information Technology", "Master", "information-technology"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
    ]),
    U("P1", "rmit-university", "RMIT University", "AU", "Melbourne", "https://www.rmit.edu.au", ["RMIT"], "School of Computing Technologies", [
        P("master-of-information-technology", "Master of Information Technology", "Master", "information-technology"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
    ]),
    U("P1", "macquarie-university", "Macquarie University", "AU", "Sydney", "https://www.mq.edu.au", ["Macquarie"], "School of Computing", [
        P("data-science", "Data Science", "Master", "data-science"),
        P("information-technology", "Information Technology", "Master", "information-technology"),
    ]),
    U("P2", "deakin-university", "Deakin University", "AU", "Melbourne", "https://www.deakin.edu.au", ["Deakin"], "School of Information Technology", [
        P("information-technology", "Information Technology", "Master", "information-technology"),
        P("data-science", "Data Science", "Master", "data-science"),
    ]),
    U("P2", "curtin-university", "Curtin University", "AU", "Perth", "https://www.curtin.edu.au", ["Curtin"], "School of Electrical Engineering, Computing and Mathematical Sciences", [
        P("computing", "Computing", "Master", "cs"),
        P("data-science", "Data Science", "Master", "data-science"),
    ]),
    # New Zealand
    U(None, "university-of-auckland", "University of Auckland", "NZ", "Auckland", "https://www.auckland.ac.nz", ["Auckland"], "School of Computer Science", [
        P("master-of-information-technology", "Master of Information Technology", "Master", "information-technology"),
        P("data-science", "Data Science", "Master", "data-science"),
    ]),
    U(None, "victoria-university-of-wellington", "Victoria University of Wellington", "NZ", "Wellington", "https://www.wgtn.ac.nz", ["Wellington", "VUW"], "School of Engineering and Computer Science", [
        P("master-of-computer-science", "Master of Computer Science", "Master", "cs"),
    ]),
    U(None, "university-of-canterbury", "University of Canterbury", "NZ", "Christchurch", "https://www.canterbury.ac.nz", ["Canterbury", "UC"], "Department of Computer Science and Software Engineering", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("applied-data-science", "Applied Data Science", "Master", "data-science"),
    ]),
    U(None, "university-of-otago", "University of Otago", "NZ", "Dunedin", "https://www.otago.ac.nz", ["Otago"], "Department of Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("applied-science", "Applied Science", "Master", "cs"),
    ]),
    U(None, "university-of-waikato", "University of Waikato", "NZ", "Hamilton", "https://www.waikato.ac.nz", ["Waikato"], "School of Computing and Mathematical Sciences", [
        P("master-of-computer-science", "Master of Computer Science", "Master", "cs"),
    ]),
    U(None, "massey-university", "Massey University", "NZ", "Palmerston North", "https://www.massey.ac.nz", ["Massey"], "School of Mathematical and Computational Sciences", [
        P("information-sciences", "Information Sciences", "Master", "cs"),
    ]),
    # Singapore
    U("P0", "national-university-of-singapore", "National University of Singapore", "SG", "Singapore", "https://www.nus.edu.sg", ["NUS"], "School of Computing", [
        P("master-of-computing-computer-science", "Master of Computing – Computer Science", "Master", "cs"),
        P("master-of-computing-artificial-intelligence", "Master of Computing – Artificial Intelligence", "Master", "ai"),
        P("master-of-computing-infocomm-security", "Master of Computing – Infocomm Security", "Master", "cs"),
    ]),
    U("P0", "nanyang-technological-university", "Nanyang Technological University", "SG", "Singapore", "https://www.ntu.edu.sg", ["NTU"], "College of Computing and Data Science", [
        P("msc-artificial-intelligence", "MSc Artificial Intelligence", "MSc", "ai"),
        P("msc-data-science", "MSc Data Science", "MSc", "data-science"),
    ]),
    U("P1", "singapore-management-university", "Singapore Management University", "SG", "Singapore", "https://www.smu.edu.sg", ["SMU"], "School of Computing and Information Systems", [
        P("master-of-it-in-business", "Master of IT in Business", "Master", "information-technology"),
    ]),
    # Japan. Existing IST departments stay; this adds EEIS and the other schools.
    U("P0", "university-of-tokyo", "The University of Tokyo", "JP", "Tokyo", "https://www.u-tokyo.ac.jp", ["UTokyo", "Todai", "University of Tokyo"], "Department of Electrical Engineering and Information Systems", [
        P("msc-eeis", "Electrical Engineering and Information Systems", "Master", "cs"),
    ], local="東京大学"),
    U("P0", "kyoto-university", "Kyoto University", "JP", "Kyoto", "https://www.kyoto-u.ac.jp", ["Kyoto"], "Graduate School of Informatics", [
        P("graduate-school-of-informatics", "Graduate School of Informatics", "Master", "cs"),
    ], local="京都大学"),
    U("P0", "institute-of-science-tokyo", "Institute of Science Tokyo", "JP", "Tokyo", "https://www.isct.ac.jp", ["Science Tokyo", "Tokyo Tech"], "School of Computing", [
        P("school-of-computing", "School of Computing", "Master", "cs"),
        P("information-and-communications", "Information and Communications", "Master", "cs"),
    ], local="東京科学大学"),
    U("P0", "osaka-university", "Osaka University", "JP", "Osaka", "https://www.osaka-u.ac.jp", ["Osaka", "Handai"], "Graduate School of Information Science and Technology", [
        P("graduate-school-of-information-science-and-technology", "Graduate School of Information Science and Technology", "Master", "cs"),
    ], local="大阪大学"),
    U("P0", "tohoku-university", "Tohoku University", "JP", "Sendai", "https://www.tohoku.ac.jp", ["Tohoku"], "Graduate School of Information Sciences", [
        P("graduate-school-of-information-sciences", "Graduate School of Information Sciences", "Master", "cs"),
    ], local="東北大学"),
    U("P0", "nagoya-university", "Nagoya University", "JP", "Nagoya", "https://www.nagoya-u.ac.jp", ["Nagoya"], "Graduate School of Informatics", [
        P("graduate-school-of-informatics", "Graduate School of Informatics", "Master", "cs"),
    ], local="名古屋大学"),
    U("P0", "kyushu-university", "Kyushu University", "JP", "Fukuoka", "https://www.kyushu-u.ac.jp", ["Kyushu"], "Graduate School of Information Science and Electrical Engineering", [
        P("information-science-and-electrical-engineering", "Information Science and Electrical Engineering", "Master", "cs"),
    ], local="九州大学"),
    U("P0", "university-of-tsukuba", "University of Tsukuba", "JP", "Tsukuba", "https://www.tsukuba.ac.jp", ["Tsukuba"], "Systems and Information Engineering", [
        P("systems-and-information-engineering", "Systems and Information Engineering", "Master", "cs"),
    ], local="筑波大学"),
    U("P0", "nara-institute-of-science-and-technology", "Nara Institute of Science and Technology", "JP", "Ikoma", "https://www.naist.jp", ["NAIST"], "Information Science", [
        P("information-science", "Information Science", "Master", "cs"),
    ], local="奈良先端科学技術大学院大学"),
    U("P0", "japan-advanced-institute-of-science-and-technology", "Japan Advanced Institute of Science and Technology", "JP", "Nomi", "https://www.jaist.ac.jp", ["JAIST"], "Information Science", [
        P("information-science", "Information Science", "Master", "cs"),
    ], local="北陸先端科学技術大学院大学"),
    U("P1", "hokkaido-university", "Hokkaido University", "JP", "Sapporo", "https://www.hokudai.ac.jp", ["Hokkaido"], "Graduate School of Information Science and Technology", [
        P("information-science-and-technology", "Information Science and Technology", "Master", "cs"),
    ], local="北海道大学"),
    U("P1", "kobe-university", "Kobe University", "JP", "Kobe", "https://www.kobe-u.ac.jp", ["Kobe"], "Graduate School of System Informatics", [
        P("system-informatics", "System Informatics", "Master", "cs"),
    ], local="神戸大学"),
    U("P1", "hiroshima-university", "Hiroshima University", "JP", "Higashihiroshima", "https://www.hiroshima-u.ac.jp", ["Hiroshima"], "Graduate School of Advanced Science and Engineering", [
        P("advanced-science-and-engineering", "Advanced Science and Engineering", "Master", "cs"),
    ], local="広島大学"),
    U("P1", "waseda-university", "Waseda University", "JP", "Tokyo", "https://www.waseda.jp", ["Waseda"], "Graduate School of Fundamental Science and Engineering", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("communications", "Communications", "Master", "cs"),
        P("fundamental-science", "Fundamental Science", "Master", "cs"),
    ], local="早稲田大学"),
    U("P1", "keio-university", "Keio University", "JP", "Tokyo", "https://www.keio.ac.jp", ["Keio"], "Graduate School of Science and Technology", [
        P("science-and-technology", "Science and Technology", "Master", "cs"),
        P("information-and-computer-science", "Information and Computer Science", "Master", "cs"),
    ], local="慶應義塾大学"),
    U("P1", "tokyo-university-of-science", "Tokyo University of Science", "JP", "Tokyo", "https://www.tus.ac.jp", ["TUS"], "Graduate School of Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("information-sciences", "Information Sciences", "Master", "cs"),
    ], local="東京理科大学"),
    U("P1", "sophia-university", "Sophia University", "JP", "Tokyo", "https://www.sophia.ac.jp", ["Sophia"], "Graduate School of Science and Technology", [
        P("information-and-communication-sciences", "Information and Communication Sciences", "Master", "cs"),
    ], local="上智大学"),
    U("P1", "ritsumeikan-university", "Ritsumeikan University", "JP", "Kyoto", "https://www.ritsumei.ac.jp", ["Ritsumeikan"], "Graduate School of Information Science and Engineering", [
        P("information-science-and-engineering", "Information Science and Engineering", "Master", "cs"),
    ], local="立命館大学"),
    U("P2", "university-of-electro-communications", "University of Electro-Communications", "JP", "Chofu", "https://www.uec.ac.jp", ["UEC"], "Graduate School of Informatics and Engineering", [
        P("informatics", "Informatics", "Master", "cs"),
        P("computer-science", "Computer Science", "Master", "cs"),
    ], local="電気通信大学"),
    U("P2", "yokohama-national-university", "Yokohama National University", "JP", "Yokohama", "https://www.ynu.ac.jp", ["YNU"], "Graduate School of Engineering Science", [
        P("information", "Information", "Master", "cs"),
        P("engineering", "Engineering", "Master", "cs"),
    ], local="横浜国立大学"),
    U("P2", "chiba-university", "Chiba University", "JP", "Chiba", "https://www.chiba-u.jp", ["Chiba"], "Graduate School of Informatics", [
        P("informatics", "Informatics", "Master", "cs"),
    ], local="千葉大学"),
    U("P2", "osaka-metropolitan-university", "Osaka Metropolitan University", "JP", "Osaka", "https://www.omu.ac.jp", ["OMU"], "Graduate School of Informatics", [
        P("informatics", "Informatics", "Master", "cs"),
    ], local="大阪公立大学"),
    U("P2", "tokyo-metropolitan-university", "Tokyo Metropolitan University", "JP", "Tokyo", "https://www.tmu.ac.jp", ["TMU"], "Graduate School of Systems Design", [
        P("computer-science", "Computer Science", "Master", "cs"),
    ], local="東京都立大学"),
    U("P2", "hosei-university", "Hosei University", "JP", "Tokyo", "https://www.hosei.ac.jp", ["Hosei"], "Graduate School of Computer and Information Sciences", [
        P("computer-and-information-sciences", "Computer and Information Sciences", "Master", "cs"),
    ], local="法政大学"),
    # Korea
    U(None, "kaist", "KAIST", "KR", "Daejeon", "https://www.kaist.ac.kr", ["KAIST"], "School of Computing", [
        P("computer-science", "Computer Science", "Master", "cs"),
    ]),
    U(None, "seoul-national-university", "Seoul National University", "KR", "Seoul", "https://www.snu.ac.kr", ["SNU"], "Department of Computer Science and Engineering", [
        P("computer-science-and-engineering", "Computer Science and Engineering", "Master", "cs"),
    ], local="서울대학교"),
    U(None, "postech", "POSTECH", "KR", "Pohang", "https://www.postech.ac.kr", ["POSTECH"], "Department of Computer Science and Engineering", [
        P("computer-science-and-engineering", "Computer Science and Engineering", "Master", "cs"),
    ]),
    U(None, "yonsei-university", "Yonsei University", "KR", "Seoul", "https://www.yonsei.ac.kr", ["Yonsei"], "Department of Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
    ], local="연세대학교"),
    U(None, "korea-university", "Korea University", "KR", "Seoul", "https://www.korea.ac.kr", ["Korea University"], "Department of Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
    ], local="고려대학교"),
    U(None, "sungkyunkwan-university", "Sungkyunkwan University", "KR", "Seoul", "https://www.skku.edu", ["SKKU"], "Department of Computer Science and Engineering", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
    ], local="성균관대학교"),
    U(None, "hanyang-university", "Hanyang University", "KR", "Seoul", "https://www.hanyang.ac.kr", ["Hanyang"], "Department of Computer Science", [
        P("computer-science", "Computer Science", "Master", "cs"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
    ], local="한양대학교"),
    U(None, "unist", "UNIST", "KR", "Ulsan", "https://www.unist.ac.kr", ["UNIST"], "Department of Computer Science and Engineering", [
        P("computer-science-and-engineering", "Computer Science and Engineering", "Master", "cs"),
    ]),
    U(None, "dgist", "DGIST", "KR", "Daegu", "https://www.dgist.ac.kr", ["DGIST"], "Graduate School", [
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
        P("information-and-communication-engineering", "Information and Communication Engineering", "Master", "cs"),
    ]),
    # Hong Kong
    U(None, "university-of-hong-kong", "University of Hong Kong", "HK", "Hong Kong", "https://www.hku.hk", ["HKU"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("artificial-intelligence", "Artificial Intelligence", "MSc", "ai"),
        P("data-science", "Data Science", "MSc", "data-science"),
    ], local="香港大學"),
    U(None, "hong-kong-university-of-science-and-technology", "Hong Kong University of Science and Technology", "HK", "Hong Kong", "https://hkust.edu.hk", ["HKUST"], "Department of Computer Science and Engineering", [
        P("msc-information-technology", "MSc Information Technology", "MSc", "information-technology"),
        P("big-data", "Big Data", "MSc", "data-science"),
    ], local="香港科技大學"),
    U(None, "chinese-university-of-hong-kong", "Chinese University of Hong Kong", "HK", "Hong Kong", "https://www.cuhk.edu.hk", ["CUHK"], "Department of Computer Science and Engineering", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
        P("information-engineering", "Information Engineering", "MSc", "cs"),
    ], local="香港中文大學"),
    U(None, "city-university-of-hong-kong", "City University of Hong Kong", "HK", "Hong Kong", "https://www.cityu.edu.hk", ["CityU"], "Department of Computer Science", [
        P("msc-computer-science", "MSc Computer Science", "MSc", "cs"),
    ], local="香港城市大學"),
    U(None, "hong-kong-polytechnic-university", "Hong Kong Polytechnic University", "HK", "Hong Kong", "https://www.polyu.edu.hk", ["PolyU"], "Department of Computing", [
        P("msc-information-technology", "MSc Information Technology", "MSc", "information-technology"),
        P("artificial-intelligence", "Artificial Intelligence", "MSc", "ai"),
        P("data-analytics", "Data Analytics", "MSc", "data-science"),
    ], local="香港理工大學"),
    U(None, "hong-kong-baptist-university", "Hong Kong Baptist University", "HK", "Hong Kong", "https://www.hkbu.edu.hk", ["HKBU"], "Department of Computer Science", [
        P("data-analytics", "Data Analytics", "Master", "data-science"),
        P("artificial-intelligence", "Artificial Intelligence", "Master", "ai"),
    ], local="香港浸會大學"),
]
