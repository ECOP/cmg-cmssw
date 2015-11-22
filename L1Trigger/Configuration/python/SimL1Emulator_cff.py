import FWCore.ParameterSet.Config as cms

# L1 Emulator sequence for simulation use-case
#    subsystem emulators run on the results of previous (in the hardware chain) subsystem emulator
#  
# Jim Brooke, 24 April 2008
# Vasile Mihai Ghete, 2009


# This object is used to make changes for different running scenarios. In
# this case for the Stage 1 trigger in run 2
from Configuration.StandardSequences.Eras import eras
# Note that this next file does nothing if the stage1L1Trigger era is not active, so
# it is safe to import even if the Stage 1 trigger is not required. It *MUST* be
# imported into this namespace, i.e. "from <file> import *".
from L1Trigger.Configuration.ConditionalStage1Configuration_cff import *

# ECAL TPG emulator and HCAL TPG run in the simulation sequence in order to be able 
# to use unsuppressed digis produced by ECAL and HCAL simulation, respectively
# in Configuration/StandardSequences/python/Digi_cff.py
# SimCalorimetry.Configuration.SimCalorimetry_cff
# which calls
# SimCalorimetry.Configuration.ecalDigiSequence_cff
# SimCalorimetry.Configuration.hcalDigiSequence_cff

### calorimeter emulators

# RCT (Regional Calorimeter Trigger) emulator
import L1Trigger.RegionalCaloTrigger.rctDigis_cfi
simRctDigis = L1Trigger.RegionalCaloTrigger.rctDigis_cfi.rctDigis.clone()

simRctDigis.ecalDigis = cms.VInputTag( cms.InputTag( 'simEcalTriggerPrimitiveDigis' ) )
simRctDigis.hcalDigis = cms.VInputTag( cms.InputTag( 'simHcalTriggerPrimitiveDigis' ) )

# GCT (Global Calorimeter Trigger) emulator
import L1Trigger.GlobalCaloTrigger.gctDigis_cfi
simGctDigis = L1Trigger.GlobalCaloTrigger.gctDigis_cfi.gctDigis.clone()

simGctDigis.inputLabel = 'simRctDigis'


### muon emulators 
#   Note: GMT requires input from calorimeter emulators, namely MipIsoData from GCT

# DT TP emulator
from L1Trigger.DTTrigger.dtTriggerPrimitiveDigis_cfi import *
# import L1Trigger.DTTrigger.dtTriggerPrimitiveDigis_cfi // FIXME replace above "from" when DT TPG configured from global tag
simDtTriggerPrimitiveDigis = L1Trigger.DTTrigger.dtTriggerPrimitiveDigis_cfi.dtTriggerPrimitiveDigis.clone()

simDtTriggerPrimitiveDigis.digiTag = 'simMuonDTDigis'

# CSC TP emulator
from L1Trigger.CSCCommonTrigger.CSCCommonTrigger_cfi import *
import L1Trigger.CSCTriggerPrimitives.cscTriggerPrimitiveDigis_cfi
simCscTriggerPrimitiveDigis = L1Trigger.CSCTriggerPrimitives.cscTriggerPrimitiveDigis_cfi.cscTriggerPrimitiveDigis.clone()

simCscTriggerPrimitiveDigis.CSCComparatorDigiProducer = cms.InputTag( 'simMuonCSCDigis', 'MuonCSCComparatorDigi' )
simCscTriggerPrimitiveDigis.CSCWireDigiProducer       = cms.InputTag( 'simMuonCSCDigis', 'MuonCSCWireDigi' )

# CSC Track Finder - digi track generation 
# currently used also by DT TF to generate CSCTF stubs
import L1Trigger.CSCTrackFinder.csctfTrackDigis_cfi
simCsctfTrackDigis = L1Trigger.CSCTrackFinder.csctfTrackDigis_cfi.csctfTrackDigis.clone()

simCsctfTrackDigis.SectorReceiverInput = cms.untracked.InputTag( 'simCscTriggerPrimitiveDigis', 'MPCSORTED' )
simCsctfTrackDigis.DTproducer = 'simDtTriggerPrimitiveDigis'

# DT Track Finder emulator
# currently generates CSCTF stubs by running CSCTF emulator
import L1Trigger.DTTrackFinder.dttfDigis_cfi
simDttfDigis = L1Trigger.DTTrackFinder.dttfDigis_cfi.dttfDigis.clone()

simDttfDigis.DTDigi_Source  = 'simDtTriggerPrimitiveDigis'
simDttfDigis.CSCStub_Source = 'simCsctfTrackDigis'

# CSC Track Finder emulator 
import L1Trigger.CSCTrackFinder.csctfDigis_cfi
simCsctfDigis = L1Trigger.CSCTrackFinder.csctfDigis_cfi.csctfDigis.clone()

simCsctfDigis.CSCTrackProducer = 'simCsctfTrackDigis'

# RPC PAC Trigger emulator
from L1Trigger.RPCTrigger.rpcTriggerDigis_cff import *
simRpcTriggerDigis = L1Trigger.RPCTrigger.rpcTriggerDigis_cff.rpcTriggerDigis.clone()

simRpcTriggerDigis.label = 'simMuonRPCDigis'

# Global Muon Trigger emulator
import L1Trigger.GlobalMuonTrigger.gmtDigis_cfi
simGmtDigis = L1Trigger.GlobalMuonTrigger.gmtDigis_cfi.gmtDigis.clone()

simGmtDigis.DTCandidates   = cms.InputTag( 'simDttfDigis', 'DT' )
simGmtDigis.CSCCandidates  = cms.InputTag( 'simCsctfDigis', 'CSC' )
simGmtDigis.RPCbCandidates = cms.InputTag( 'simRpcTriggerDigis', 'RPCb' )
simGmtDigis.RPCfCandidates = cms.InputTag( 'simRpcTriggerDigis', 'RPCf' )

simGmtDigis.MipIsoData     = 'simRctDigis'


### technical trigger emulators

# BSC Technical Trigger
import L1TriggerOffline.L1Analyzer.bscTrigger_cfi
simBscDigis = L1TriggerOffline.L1Analyzer.bscTrigger_cfi.bscTrigger.clone()

# RPC Technical Trigger
import L1Trigger.RPCTechnicalTrigger.rpcTechnicalTrigger_cfi
simRpcTechTrigDigis = L1Trigger.RPCTechnicalTrigger.rpcTechnicalTrigger_cfi.rpcTechnicalTrigger.clone()

simRpcTechTrigDigis.RPCDigiLabel = 'simMuonRPCDigis'

# HCAL Technical Trigger
import SimCalorimetry.HcalTrigPrimProducers.hcalTTPRecord_cfi
simHcalTechTrigDigis = SimCalorimetry.HcalTrigPrimProducers.hcalTTPRecord_cfi.simHcalTTPRecord.clone()

# CASTOR Techical Trigger
import SimCalorimetry.CastorTechTrigProducer.castorTTRecord_cfi
simCastorTechTrigDigis = SimCalorimetry.CastorTechTrigProducer.castorTTRecord_cfi.simCastorTTRecord.clone()

# Global Trigger emulator
import L1Trigger.GlobalTrigger.gtDigis_cfi
simGtDigis = L1Trigger.GlobalTrigger.gtDigis_cfi.gtDigis.clone()

simGtDigis.GmtInputTag = 'simGmtDigis'
simGtDigis.GctInputTag = 'simGctDigis'
simGtDigis.TechnicalTriggersInputTags = cms.VInputTag(
    cms.InputTag( 'simBscDigis' ), 
    cms.InputTag( 'simRpcTechTrigDigis' ),
    cms.InputTag( 'simHcalTechTrigDigis' ),
    cms.InputTag( 'simCastorTechTrigDigis' )
    )
#
# Make some changes if using the Stage 1 trigger
#

### L1 Trigger sequences

SimL1MuTriggerPrimitives = cms.Sequence( 
    simDtTriggerPrimitiveDigis + 
    simCscTriggerPrimitiveDigis )

SimL1MuTrackFinders = cms.Sequence( 
    simCsctfTrackDigis + 
    simDttfDigis + 
    simCsctfDigis )

SimL1TechnicalTriggers = cms.Sequence( 
    simBscDigis + 
    simRpcTechTrigDigis + 
    simHcalTechTrigDigis +
    simCastorTechTrigDigis )

SimL1Emulator = cms.Sequence(
    simRctDigis + 
    simGctDigis + 
    SimL1MuTriggerPrimitives + 
    SimL1MuTrackFinders + 
    simRpcTriggerDigis + 
    simGmtDigis + 
    SimL1TechnicalTriggers + 
    simGtDigis )

### Stage 1 modifications
from L1Trigger.L1TCalorimeter.simRctUpgradeFormatDigis_cfi import *
from L1Trigger.L1TCalorimeter.simCaloStage1Digis_cfi import *
from L1Trigger.L1TCalorimeter.simCaloStage1FinalDigis_cfi import *
from L1Trigger.L1TCalorimeter.simCaloStage1LegacyFormatDigis_cfi import *

# we no longer load emulator parameters from L1Trigger/L1TCalorimeter/python/L1TCaloStage1_cff.py because this is fundamentally wrong

def _modifySimL1EmulatorForStage1Trigger( SimL1Emulator_object ) :
    print "Modifying SimL1Emulator for stage 1"
    L1TStage1EmulatorSeq = cms.Sequence( simRctUpgradeFormatDigis
                                     +simCaloStage1Digis
                                     +simCaloStage1FinalDigis
                                     +simCaloStage1LegacyFormatDigis )
    SimL1Emulator_object.replace( simGctDigis, L1TStage1EmulatorSeq )

eras.stage1L1Trigger.toModify( SimL1Emulator, func=_modifySimL1EmulatorForStage1Trigger )
eras.stage1L1Trigger.toModify( simGtDigis, GctInputTag = 'simCaloStage1LegacyFormatDigis' )
eras.stage1L1Trigger.toModify( simGtDigis, TechnicalTriggersInputTags = cms.VInputTag() )



### Stage 2 modifications

from L1Trigger.L1TCalorimeter.simCaloStage2Layer1Digis_cfi import simCaloStage2Layer1Digis
from L1Trigger.L1TCalorimeter.simCaloStage2Digis_cfi import simCaloStage2Digis

def _modifySimL1EmulatorForStage2Trigger( SimL1Emulator_object ) :
    print "Modifying SimL1Emulator for stage 2"
    SimL1Emulator_object.replace( simRctDigis, simCaloStage2Layer1Digis )
    SimL1Emulator_object.replace( simGctDigis, simCaloStage2Digis )

eras.stage2L1Trigger.toModify( SimL1Emulator, func=_modifySimL1EmulatorForStage2Trigger )





