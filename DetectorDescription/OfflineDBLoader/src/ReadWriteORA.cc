#include "DetectorDescription/OfflineDBLoader/interface/ReadWriteORA.h"

#include "DetectorDescription/Parser/interface/DDLParser.h"
#include "DetectorDescription/Parser/interface/DDLConfiguration.h"
#include "DetectorDescription/Base/interface/DDException.h"
#include "DetectorDescription/PersistentDDDObjects/interface/PersistentDDDObjects.h"
#include "DetectorDescription/PersistentDDDObjects/interface/IOVMeta.h"
#include "DetectorDescription/DBReader/interface/DDORAReader.h"
#include "DetectorDescription/PersistentDDDObjects/interface/DDDToPersFactory.h"
#include "DetectorDescription/Core/interface/DDCompactView.h"
#include "DetectorDescription/Core/interface/DDRoot.h"

#include "POOLCore/POOLContext.h"
#include "PluginManager/PluginManager.h"
#include "FileCatalog/URIParser.h"
#include "FileCatalog/IFileCatalog.h"
#include "DataSvc/IDataSvc.h"
#include "DataSvc/DataSvcFactory.h"
#include "PersistencySvc/DatabaseConnectionPolicy.h"
#include "StorageSvc/DbType.h"
#include "PersistencySvc/ISession.h"
#include "PersistencySvc/ITransaction.h"
#include "DataSvc/Ref.h"

#include "SealUtil/SealTimer.h"
#include "SealBase/ShellEnvironment.h"

#include<string>

ReadWriteORA::ReadWriteORA ( const std::string& dbConnectString
			     , const std::string& xmlConfiguration 
			     , const std::string& name 
			     , const std::string& type
			     , const std::string& userName
			     , const std::string& password )
  : dbConnectString_(dbConnectString)
    , xmlConfiguration_(xmlConfiguration)
    , name_(name)
    , type_(type)
    , userName_(userName)
    , password_(password)
{ 
  //FIXME: check DB and xml for existence, nothing more.

}

ReadWriteORA::~ReadWriteORA () { }

/// Read from XML and write using POOL Object Relational Access
bool ReadWriteORA::writeDB ( ) {

  seal::PluginManager::get()->initialise();
  seal::SealTimer t("ReadWriteORA::WriteFromMemoryToDB");

  try {

    //       seal::ShellEnvironment senv;
    //       senv.set( "POOL_AUTH_USER", userName_ );
    //       senv.set( "POOL_AUTH_PASSWORD", password_ );
    //       if ( senv.has("DDWriteConnectString") ) {
    // 	dbConnectString_ = senv.get("DDWriteConnectString");
    // 	cout << "Environment variable DDWriteConnectString was used for connection. ";
    //       }
    //       cout << "Connection String is: "  << dbConnectString_ << endl;
      
    // Loads the seal message stream
    pool::POOLContext::loadComponent( "SEAL/Services/MessageService" );
    pool::POOLContext::loadComponent( "POOL/Services/EnvironmentAuthenticationService" );

    // Parsing URI for catalog and opening the catalog
    pool::URIParser p;
    p.parse();

    pool::IFileCatalog lcat;
    pool::IFileCatalog * cat = &lcat;
    cat->setWriteCatalog(p.contactstring());
    cat->connect();
    cat->start();
    
    pool::IDataSvc *svc = pool::DataSvcFactory::instance(cat);

    // Define the policy for the implicit file handling
    pool::DatabaseConnectionPolicy policy;
    policy.setWriteModeForNonExisting(pool::DatabaseConnectionPolicy::CREATE);
    policy.setWriteModeForExisting(pool::DatabaseConnectionPolicy::UPDATE);
    svc->session().setDefaultConnectionPolicy(policy);

    long int tech(pool::POOL_RDBMS_StorageType.type()); // pool::ROOTKEY_StorageType.type()
    svc->transaction().start(pool::ITransaction::UPDATE);

    pool::Ref<PIdealGeometry> pgeom(svc, new PIdealGeometry);

    pool::Placement geomPlace(dbConnectString_, pool::DatabaseSpecification::PFN, type_, pool::Guid::null(), tech);
 
    // This will also register the file. For this to occur, the placement object must use a PFN.
    pgeom.markWrite(geomPlace);

    std::string iovtoken=pgeom.toString();

    // Grab the DDD compact view that is in memory and write it on out!
    DDCompactView cpv;
    
    DDCompactView::graph_type gra = cpv.graph();
    
    //   DDSpecifics::iterator<DDSpecifics> it(DDSpecifics::begin()), ed(DDSpecifics::end());
    //   for (; it != ed; ++it) {
    //     if (! it->isDefined().second) continue;  
    //     const DDSpecifics & sp = *it;
    //     //    os << "--Spec: @ ";
    //     nameout(os,sp.name());
    //     //    os << ' ' << sp.selection().size() << endl;
    //     vector<DDPartSelection>::const_iterator sit(sp.selection().begin()), sed(sp.selection().end());
    //     for (; sit != sed; ++sit) {
    //       os << *sit << endl;
    //     }
    //     os << sp.specifics().size() << endl;
    //     DDsvalues_type::const_iterator vit(sp.specifics().begin()), ved(sp.specifics().end());
    //     for (; vit != ved; ++vit) {
    //       const DDValue & v = vit->second;
    //       os << ' ' << '"' << v.name() << '"' << ' ';
    //       if (v.isEvaluated()) {
    //         os << 1 << ' ';
    //       }
    //       else {
    //         os << 0 << ' ';
    //       }
    //       os << v.size() << ' ';
    //       if (v.isEvaluated()) {
    //         size_t s=v.size();
    // 	size_t i=0;
    // 	for (; i<s; ++i) {
    // 	  os << '"' << v[i].first << '"' << ' ' << v[i].second << ' ';
    // 	}
    //       }
    //       else {
    //         size_t s=v.size();
    // 	size_t i=0;
    // 	const vector<string> & vs = v.strings();
    // 	for (; i<s; ++i) {
    // 	  os << '"' << vs[i] << '"' << ' ';
    //         }
    //       }
    //       os << endl;
      
    //     }
    //   }  

    typedef graph_type::const_adj_iterator adjl_iterator;
    adjl_iterator git = gra.begin();
    adjl_iterator gend = gra.end();    
    
    graph_type::index_type i=0;
    PLogicalPart* plp;
    for (; git != gend; ++git) 
      {
	const DDLogicalPart & ddLP = gra.nodeData(git);
	plp = DDDToPersFactory::logicalPart ( ddLP  );
	pgeom->pLogicalParts.push_back( *plp );
	delete plp;
	++i;
	if (git->size()) 
	  {
	    // ask for children of ddLP  
	    graph_type::edge_list::const_iterator cit  = git->begin();
	    graph_type::edge_list::const_iterator cend = git->end();
	    PPosPart* ppp;
	    for (; cit != cend; ++cit) 
	      {
		const DDLogicalPart & ddcurLP = gra.nodeData(cit->first);
		ppp = DDDToPersFactory::position ( ddLP, ddcurLP, gra.edgeData(cit->second) );
		pgeom->pPosParts.push_back( *ppp );
		delete ppp;
	      } // iterate over children
	  } // if (children)
      } // iterate over graph nodes  
  

    DDMaterial::iterator<DDMaterial> it(DDMaterial::begin()), ed(DDMaterial::end());
    PMaterial* pm;
    for (; it != ed; ++it) {
      if (! it->isDefined().second) continue;
      pm = DDDToPersFactory::material ( *it );
      pgeom->pMaterials.push_back ( *pm );
      delete pm;
    }

    DDRotation::iterator<DDRotation> rit(DDRotation::begin()), red(DDRotation::end());
    PRotation* pr;
    for (; rit != red; ++rit) {
      if (! rit->isDefined().second) continue;  
      pr = DDDToPersFactory::rotation(*rit);
      pgeom->pRotations.push_back ( *pr );
    } 

    DDSolid::iterator<DDSolid> sit(DDSolid::begin()), sed(DDSolid::end());
    PSolid* ps;
    for (; sit != sed; ++sit) {
      if (! sit->isDefined().second) continue;  
      ps = DDDToPersFactory::solid( *sit );
      pgeom->pSolids.push_back( *ps );
      delete ps;
    }

    pgeom->pStartNode = DDRootDef::instance().root().toString();
    std::cout << "commit catalog" << std::endl;
    cat->commit();
    svc->transaction().commit();
    std::cout << "committed" << std::endl;
    svc->session().disconnectAll();
    std::cout << "disconnected" << endl;

    // using IOVMeta to translate name to token.
    IOVMeta meta (dbConnectString_);
    std::cout << "Pool token = \"" << iovtoken << "\"" << std::endl;
    if ( meta.getIOVToken(name_) != "" ) {
      std::cout<<"Mapping exists!  WARNING: Nothing done, map remains as it was." << std::endl;
      std::cout<<"TABLE IOVMETA contains an un-named token.  You can copy the token down and fix the DB."<<std::endl;
    }else{
      meta.addMapping(name_, iovtoken);
    }

    delete svc;

  }
  catch ( seal::Exception& e ) {
    std::cout << e.what() << std::endl;
    return false;
  }
  catch ( std::exception& e ) {
    std::cout << e.what() << std::endl;
    return false;
  }
  catch ( ... ) {
    std::cout << "Funny error" << std::endl;
    return false;
  }

  return true;
}

/// Read from XML files
bool ReadWriteORA::readFromXML ( ) {
  seal::SealTimer t("ReadWriteORA::readFromXML");
  DDLParser* myP = DDLParser::instance();
  DDLConfiguration dp;
  cout << "About to read configuration file: " << xmlConfiguration_ << endl; 
  int success = dp.readConfig(xmlConfiguration_);
  if ( success != 0) {
    throw DDException("Failed to read configuration.");
  }
  success = myP->parse(dp);
  if ( success != 0) {
    throw DDException("Failed to parse whole geometry!");
  }
  return true;
}

/// Read back from the persistent objects
bool ReadWriteORA::readFromDB ( ) {

  IOVMeta meta(dbConnectString_);

  cout << "Looking for ..." << name_ << endl;
  std::string iovAToken= meta.getIOVToken(name_);
  seal::SealTimer timer("ReadWriteORA::readFromDB");
  DDORAReader ddorar( "cms:OCMS", 
		      iovAToken,
		      userName_, 
		      password_,
		      dbConnectString_ );
  ddorar.readDB();
  return true;
}
