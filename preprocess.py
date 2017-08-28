#!/usr/bin/env python
# usage: 
# ./case_keywords.py -f processed_queries_7m_unk.txt

from __future__ import print_function
from argparse import ArgumentParser
import re, subprocess
from sys import stdout

keywords = ["GROUP", "TOP", "CROSS", "INTO", "WITH", "BY", "SELECT", "CASE", "ACCESS", "NULL", "CREATE", "ORDER", "TABLE", "LEFT", "OUTER", "EXISTS", "AS", "INNER", "IN", "ELSE", "WHERE", "FROM", "ON", "ALL", "JOIN", "LIKE", "DISTINCT", "HAVING"]

functions = ["ABS", "AVG", "COUNT", "MAX", "MIN", "SQRT", "SUM", "TRIM"]

space_keywords = ["WHERE", "GROUP", "JOIN", "ORDER"]

keywords_to_case = ['COUNT', 'ACCESS', 'DEC', 'END', 'MIN', 'MAX', 'IS', 'WHEN', 'ASC', 'CAST', 'ABS', 'THEN', 'DESC', 'NOT', 'AVG', 'WHERE', 'FIRST']
keywords_to_case = set(keywords_to_case)

quoted = ["'Neighbors'", "'SpecObjAll'", "'Galaxy'", "'SpecPhotoAll'", "'photoObjAll'", "'Star'", "'PhotoObjAll'", "'sdssTilingGeometry'", "'sdssTileAll'", "'galSpecExtra'", "'STAR'", "'PhotoTag'", "'galSpecInfo'", "'Region2Box'", "'mangaDrpAll'", "'sdssTiledTargetAll'", "'FieldProfile'", "'Field'", "'PlateX'", "'galSpecLine'", "'PhotoProfile'", "'GALAXY'", "'SpecobjAll'"]

unknown = ["SpecClass", "Photoz2", "specobjall", "zConf", "XCRedshift", "\[DEC\]", "BestObjid"]

# quoted_not_tables = ["'TilingGeometry'", "'Segment'", "'Match'", "'QSO'", "'U'"]
# alias2 = ['S1', 'S2', 'GN']

# num objects in schema -> seen in corpus
# tables 124 -> 115
# views 59 -> 51
# funcs 246 -> 205
# columns 5247 -> 853
sdss_tables = ['apogeeDesign', 'apogeeField', 'apogeeObject', 'apogeePlate', 'apogeeStar', 'apogeeStarAllVisit', 'apogeeStarVisit', 'apogeeVisit', 'aspcapStar', 'aspcapStarCovar', 'AtlasOutline', 'DataConstants', 'DBColumns', 'DBObjects', 'DBViewCols', 'Dependency', 'detectionIndex', 'Diagnostics', 'emissionLinesPort', 'Field', 'FieldProfile', 'FileGroupMap', 'FIRST', 'Frame', 'galSpecExtra', 'galSpecIndx', 'galSpecInfo', 'galSpecLine', 'HalfSpace', 'History', 'IndexMap', 'Inventory', 'LoadHistory', 'mangaDrpAll', 'mangatarget', 'marvelsStar', 'Mask', 'MaskedObject', 'Neighbors', 'nsatlas', 'PartitionMap', 'PhotoObjAll', 'PhotoObjDR7', 'PhotoPrimaryDR7', 'PhotoProfile', 'Photoz', 'Plate2Target', 'PlateX', 'ProfileDefs', 'ProperMotions', 'PubHistory', 'RC3', 'RecentQueries', 'Region', 'Region2Box', 'RegionArcs', 'RegionPatch', 'RegionTypes', 'Rmatrix', 'ROSAT', 'Run', 'RunShift', 'sdssBestTarget2Sector', 'SDSSConstants', 'sdssImagingHalfSpaces', 'sdssPolygon2Field', 'sdssPolygons', 'sdssSector', 'sdssSector2Tile', 'sdssTargetParam', 'sdssTileAll', 'sdssTiledTargetAll', 'sdssTilingGeometry', 'sdssTilingInfo', 'sdssTilingRun', 'segueTargetAll', 'SiteConstants', 'SiteDBs', 'SiteDiagnostics', 'SpecDR7', 'SpecObjAll', 'SpecPhotoAll', 'sppLines', 'sppParams', 'sppTargets', 'stellarMassFSPSGranEarlyDust', 'stellarMassFSPSGranEarlyNoDust', 'stellarMassFSPSGranWideDust', 'stellarMassFSPSGranWideNoDust', 'stellarMassPassivePort', 'stellarMassPCAWiscBC03', 'stellarMassPCAWiscM11', 'stellarMassStarformingPort', 'StripeDefs', 'Target', 'TargetInfo', 'thingIndex', 'TwoMass', 'TwoMassXSC', 'USNO', 'Versions', 'WISE_allsky', 'WISE_xmatch', 'wiseForcedTarget', 'Zone', 'zoo2MainPhotoz', 'zoo2MainSpecz', 'zoo2Stripe82Coadd1', 'zoo2Stripe82Normal', 'zooConfidence', 'zooMirrorBias', 'zooMonochromeBias', 'zooNoSpec', 'zooSpec', 'zooVotes']
sdss_views = ['AncillaryTarget1', 'AncillaryTarget2', 'ApogeeAspcapFlag', 'ApogeeStarFlag', 'ApogeeTarget1', 'BossTarget1', 'CalibStatus', 'Columns', 'CoordType', 'FieldQuality', 'FramesStatus', 'Galaxy', 'GalaxyTag', 'HoleType', 'ImageStatus', 'InsideMask', 'MaskType', 'PhotoFamily', 'PhotoFlags', 'PhotoMode', 'PhotoObj', 'PhotoPrimary', 'PhotoSecondary', 'PhotoStatus', 'PhotoTag', 'PhotoType', 'PrimTarget', 'ProgramType', 'PspStatus', 'RegionConvex', 'ResolveStatus', 'sdssTile', 'sdssTilingBoundary', 'sdssTilingMask', 'SecTarget', 'segue1SpecObjAll', 'Segue1Target1', 'segue2SpecObjAll', 'Segue2Target1', 'segueSpecObjAll', 'Sky', 'SourceType', 'SpecialTarget1', 'SpecObj', 'SpecPhoto', 'SpecPixMask', 'SpecZWarning', 'Star', 'StarTag', 'TableDesc', 'TiMask', 'Unknown']
sdss_functions = ['fAncillaryTarget1', 'fApogeeAspcapFlag', 'fApogeeStarFlag', 'fApogeeTarget1', 'fCalibStatus', 'fCalibStatusN', 'fCamcol', 'fCoordsFromEq', 'fCoordType', 'fCoordTypeN', 'fCosmoAbsMag', 'fCosmoAgeOfUniverse', 'fCosmoComovDist2ObjectsRADEC', 'fCosmoComovDist2ObjectsXYZ', 'fCosmoComovingVolume', 'fCosmoDa', 'fCosmoDc', 'fCosmoDistanceModulus', 'fCosmoDl', 'fCosmoDm', 'fCosmoHubbleDistance', 'fCosmoLookBackTime', 'fCosmoQuantities', 'fCosmoTimeInterval', 'fCosmoZfromAgeOfUniverse', 'fCosmoZfromDa', 'fCosmoZfromDc', 'fCosmoZfromDl', 'fCosmoZfromDm', 'fCosmoZfromLookBackTime', 'fDatediffSec', 'fDistanceArcMinEq', 'fDistanceArcMinXYZ', 'fDistanceEq', 'fDistanceXyz', 'fDMS', 'fDMSbase', 'fDocColumns', 'fDocColumnsWithRank', 'fDocFunctionParams', 'fEnum', 'fEqFromMuNu', 'fEtaFromEq', 'fEtaToNormal', 'fFiber', 'fField', 'fFieldMask', 'fFieldMaskN', 'fFieldQuality', 'fFieldQualityN', 'fFirstFieldBit', 'fFootprintEq', 'fFramesStatus', 'fFramesStatusN', 'fGetAlpha', 'fGetLat', 'fGetLon', 'fGetLonLat', 'fGetNearbyApogeeStarEq', 'fGetNearbyFrameEq', 'fGetNearbyObjAllEq', 'fGetNearbyObjAllXYZ', 'fGetNearbyObjEq', 'fGetNearbyObjXYZ', 'fGetNearbySpecObjAllEq', 'fGetNearbySpecObjAllXYZ', 'fGetNearbySpecObjEq', 'fGetNearbySpecObjXYZ', 'fGetNearestFrameEq', 'fGetNearestFrameidEq', 'fGetNearestObjAllEq', 'fGetNearestObjEq', 'fGetNearestObjIdAllEq', 'fGetNearestObjIdEq', 'fGetNearestObjIdEqMode', 'fGetNearestObjIdEqType', 'fGetNearestObjXYZ', 'fGetNearestSpecObjAllEq', 'fGetNearestSpecObjAllXYZ', 'fGetNearestSpecObjEq', 'fGetNearestSpecObjIdAllEq', 'fGetNearestSpecObjIdEq', 'fGetNearestSpecObjXYZ', 'fGetObjectsEq', 'fGetObjectsMaskEq', 'fGetObjFromRect', 'fGetObjFromRectEq', 'fGetUrlExpEq', 'fGetUrlExpId', 'fGetUrlFitsAtlas', 'fGetUrlFitsBin', 'fGetUrlFitsCFrame', 'fGetUrlFitsField', 'fGetUrlFitsMask', 'fGetUrlFitsPlate', 'fGetUrlFitsSpectrum', 'fGetUrlFrameImg', 'fGetUrlNavEq', 'fGetUrlNavId', 'fGetUrlSpecImg', 'fGetWCS', 'fHMS', 'fHMSbase', 'fHoleType', 'fHoleTypeN', 'fHtmCoverBinaryAdvanced', 'fHtmCoverCircleEq', 'fHtmCoverCircleXyz', 'fHtmCoverRegion', 'fHtmCoverRegionAdvanced', 'fHtmCoverRegionError', 'fHtmEq', 'fHtmEqToXyz', 'fHtmGetCenterPoint', 'fHtmGetCornerPoints', 'fHtmGetString', 'fHtmVersion', 'fHtmXyz', 'fHtmXyzToEq', 'fIAUFromEq', 'fImageStatus', 'fImageStatusN', 'fInFootprintEq', 'fInsideMask', 'fInsideMaskN', 'fIsNumbers', 'fLambdaFromEq', 'fMagToFlux', 'fMagToFluxErr', 'fMaskType', 'fMaskTypeN', 'fMathGetBin', 'fMJD', 'fMJDToGMT', 'fMuFromEq', 'fMuNuFromEq', 'fNormalizeString', 'fNuFromEq', 'fObj', 'fObjID', 'fObjidFromSDSS', 'fObjidFromSDSSWithFF', 'fPhotoDescription', 'fPhotoFlags', 'fPhotoFlagsN', 'fPhotoMode', 'fPhotoModeN', 'fPhotoStatus', 'fPhotoStatusN', 'fPhotoType', 'fPhotoTypeN', 'fPlate', 'fPolygonsContainingPointEq', 'fPolygonsContainingPointXYZ', 'fPrimaryObjID', 'fPrimTarget', 'fPrimTargetN', 'fProgramType', 'fProgramTypeN', 'fPspStatus', 'fPspStatusN', 'fRegionContainsPointEq', 'fRegionContainsPointXYZ', 'fRegionFuzz', 'fRegionGetObjectsFromRegionId', 'fRegionGetObjectsFromString', 'fRegionOverlapId', 'fRegionsContainingPointEq', 'fRegionsContainingPointXYZ', 'fRegionsIntersectingBinary', 'fRegionsIntersectingString', 'fReplace', 'fRerun', 'fResolveStatus', 'fResolveStatusN', 'fRotateV3', 'fRun', 'fSDSS', 'fSDSSfromObjID', 'fSecTarget', 'fSecTargetN', 'fSegue1Target1', 'fSegue1Target1N', 'fSegue2Target1', 'fSegue2Target1N', 'fSkyVersion', 'fSourceType', 'fSpecDescription', 'fSpecialTarget1', 'fSpecialTarget1N', 'fSpecidFromSDSS', 'fSpecPixMask', 'fSpecPixMaskN', 'fSpecZWarning', 'fSpecZWarningN', 'fStripeOfRun', 'fStripeToNormal', 'fStripOfRun', 'fTiMask', 'fTiMaskN', 'fTokenAdvance', 'fTokenNext', 'fTokenStringToTable', 'fVarBinToHex', 'fWedgeV3']
sdss_columns = ['child', 'Plate', 'rMag', 'tai', 'psfMagErr_g', 'raErr', 'psfMagErr_i', 'psfMagErr_u', 'psfMagErr_r', 'psfMagErr_z', 'nnSpecz', 'SNR', 'coordType', 'deVABErr_z', 'deVABErr_r', 'FLAGS_i', 'deVABErr_u', 'modelFlux_g', 'modelFlux_i', 'modelFlux_u', 'modelFlux_r', 'modelFlux_z', 'h_beta_flux', 'colc_z', 'nii_6548_flux_err', 'colc_r', 'colc_u', 'colc_i', 'sigmaStarsErr', 'colc_g', 'logMass_err', 'type', 'deVFluxIvar_g', 'deVFluxIvar_i', 'f_i', 'deVFluxIvar_r', 'deVFluxIvar_u', 'p_cw', 'deVFluxIvar_z', 't_age_mean', 'probPSF_u', 'radius', 'probPSF_r', 'probPSF_z', 'probPSF_g', 'probPSF_i', 'description', 'h_delta_reqw', 'cModelFluxIvar_i', 'err_u', 'p_mg', 'err_r', 'err_z', 'err_g', 'err_i', 'sciencePrimary', 'cModelFluxIvar_g', 'p_edge', 'deVPhi_g', 'img', 'insideMask', 'band', 'skyVersion', 'l', 'logg', 'HI', 'quality', 'psfFlux_g', 'NeighborObjID', 'glat', 'ra', 'h_beta_reqw', 'sii_6731_flux', 'filter', 'TIME', 'key', 'rank', 'tau_err', 'expAB_g', 'expAB_i', 'expAB_r', 'expAB_u', 'expAB_z', 'B', 'distance', 'PMDECERR', 'tileAll', 'ROWC', 'Gerr', 'h_gamma_reqw', 'LOGGADOP', 'Metallicity', 'dr7ObjID', 'expRad_z', 'glon', 'expRad_u', 'expRad_r', 'expRad_i', 'cModelFlux_z', 'cModelFlux_u', 'cModelFlux_r', 'QA', 'oi_6300_flux', 'cModelFlux_i', 'cModelFlux_g', 'cmin', 'mRrCcErr_g', 'nChild', 'dversion', 'version', 'specobjid', 'plate', 'plateid', 'FEHADOPN', 'maskType', 'run2d', 'UMBE', 'ITE', 'cModelMag_u', 'psfFluxIvar_g', 'SECTARGET', 'cModelMag_i', 'cModelMag_g', 'FIBERMAG_z', 'FIBERMAG_r', 'FIBERMAG_u', 'FIBERMAG_g', 'fiber2Mag_i', 'deVFlux_g', 'psfFlux_r', 'deVFlux_i', 'deVFlux_u', 'deVFlux_r', 'fiber2Mag_r', 'psfFlux_i', 'velDispErr', 'b_g', 'f_z', 'FIELDID', 'CHUNK', 'petroFlux_u', 'petroFlux_r', 'b_z', 'petroFlux_z', 'petroFlux_g', 'SPECOBJID', 'petroFlux_i', 'snMedian', 'offsetDec_i', 'LERR', 'offsetDec_g', 'fiberid', 'offsetDec_z', 'offsetDec_r', 'offsetDec_u', 'id', 'a_r', 'rmin', 'mstellar_median', 'snr', 'starflag', 'd4000', 'rowc_i', 'oii_3729_flux', 'rowc_g', 'rowc_z', 'rowc_r', 'rowc_u', 'zoom', 'bpt', 'raMax', 'taiEnd', 'mRrCcPSF_i', 'mRrCcPSF_g', 'mRrCcPSF_z', 'b_u', 'mRrCcPSF_r', 'mRrCcPSF_u', 'Hr', 'Hg', 'lnLDeV_z', 'lnLDeV_u', 'lnLDeV_r', 'CAMCOL', 'lnLDeV_i', 'lnLDeV_g', 'deVMag_z', 'deVMag_r', 'deVMag_u', 'deVMag_i', 'deVMag_g', 'Flux_OI_6300', 'FeH', 'h', 'e_u', 'lnLStar_z', 'fluxObjID', 'lcolor', 'rerun', 'dered_g', 'dered_r', 'k', 'c_g', 'when', 'tid', 'nu', 'node', 'E', 'sourceType', 'vscatter', 'subclass', 'loadVersion', 'row', 'PLATE', 'sectarget', 'programname', 'PRIMTARGET', 'logMass', 'FEHADOP', 'PSFMAG_u', 'tableName', 'bc', 'pmB', 'pmL', 'BT', 'FLAG', 'MB', 'shift', 'velDisp', 'CaIIKside', 'OBJID', 'pmDecErr', 'F', 'airmass', 'obj', 'modelMag_g', 'modelMag_i', 'modelMag_r', 'modelMag_u', 'modelMag_z', 'nProf_i', 'DISTi', 'uErr_i', 'tile', 'rowcErr', 'rmax', 'dr7objid', 'mag', 'nProf_z', 'uErr_u', 'colv', 'colc', 'RV', 'RA', 'RL', 'col0', 'nvote', 'name', 'h_beta_eqw', 'apogee_target1', 'apogee_target2', 'mjd_g', 'qErr_i', 'qErr_g', 'expABErr_r', 'qErr_r', 'h_beta_flux_err', 'decMin', 'state', 'size', 'nnFarObjID', 'yBin', 'pmdec', 'a', 'sfr_tot_p50', 'f_g', 'f_u', 'FEHADOPUNC', 'r', 'f_r', 'ssfr', 'DL', 'flags_g', 'flags_i', 'flags_r', 'flags_u', 'flags_z', 'Flux_SII_6730', 'ssfr_min', 'deVRad_i', 'age_min', 'deVRad_u', 'd_g', 'FIBERID', 'PA', 'sigmaStars', 'uErr_g', 'bptclass', 'e_r', 'e_z', 'e_g', 'e_i', 'fieldID', 'rms', 'rowcErr_r', 'rowcErr_u', 'rowcErr_z', 'rowcErr_g', 'rowcErr_i', 'deVRad_g', 'aperFlux7_r', 'aperFlux7_u', 'PMRAERR', 'aperFlux7_z', 'deVRad_r', 'aperFlux7_g', 'aperFlux7_i', 'deVRad_z', 'parent', 'Flux_NII_6583', 'expPhi_i', 'expPhi_g', 'PROGRAMNAME', 'expPhi_z', 'expPhi_u', 'expPhi_r', 'dered_i', 'jd', 'pmra', 'mRrCcPsf_r', 'photoStatus', 'pmRa', 'FIELD', 'pmDec', 'RUN', 'dered_z', 'TYPE', 'j', 'dered_u', 'status', 'primtarget', 'ID', 'programType', 'oii_3726_flux', 'deVAB_i', 'deVAB_g', 'deVAB_z', 'deVAB_r', 'deVAB_u', 'instrument', 'skyErr_r', 'code', 'fieldList', 'teff', 'ellip', 'skyErr_g', 'mCr4PSF_i', 'mCr4PSF_g', 'mCr4PSF_z', 'mCr4PSF_u', 'mCr4PSF_r', 'extinction_i', 'petroR50_i', 'petroR50_g', 'extinction_g', 'extinction_z', 'petroR50_z', 'petroR50_u', 'extinction_r', 'extinction_u', 'petroR50_r', 'redshift', 'PMDEC', 'strip', 'uErr_r', 'area', 'J', 'RUN2D', 'file', 'calibStatus_g', 'field', 'calibStatus_r', 'expFluxIvar_z', 'expFluxIvar_r', 'expFluxIvar_u', 'secTarget', 'expFluxIvar_g', 'mask', 'vhelio', 'u', 'w1mpro', 'MJD', 'verr', 'Flux_SII_6716', 'd_z', 'd_r', 'disti', 'd_i', 'petroR90_r', 'petroR90_u', 'foreignKey', 'petroR90_z', 'nii_6548_flux', 'value', 'petroR90_g', 'petroR90_i', 'integr', 'mE1E2Err_z', 'mE2_i', 'mE1E2Err_r', 'mE2_g', 'mE1E2Err_u', 'mE1E2Err_i', 'mE2_z', 'mE2_u', 'mE2_r', 'mE1E2Err_g', 'oii_3729_flux_err', 'mRrCc_u', 'TARGETOBJID', 'petroFluxIvar_r', 'petroFluxIvar_u', 'PMRA', 'petroFluxIvar_z', 'petroFluxIvar_g', 'petroFluxIvar_i', 'minor', 'c_i', 'c_r', 'c_u', 'c_z', 'htmID', 'dec', 'photoRa', 'CAT', 'DATE', 'cntr', 'AIB', 'type_g', 'EXTINCTION_i', 'type_i', 'subClass', 'type_r', 'type_u', 'type_z', 'deVMagErr_r', 'deVMagErr_u', 'deVMagErr_z', 'deVMagErr_g', 'deVMagErr_i', 'nnObjID', 'RERUN', 'CaIIKerr', 'regionid', 'PLATEID', 'skyErr_i', 'L', 'neighborType', 'skyErr_z', 'SFR', 'mE1_i', 'BESTOBJID', 'mE1_g', 'mE1_z', 'mE1_r', 'event', 'mE1_u', 'FIBER', 'zErr', 'aspcapflag', 'major', 'dr8objid', 'objid', 'MATCH', 'b', 'SURVEY', 'age_mean', 'expMagErr_i', 'tau_mean', 'DELTA', 'cModelMagErr_r', 'expMagErr_g', 'expMagErr_z', 'expMagErr_r', 'expMagErr_u', 'Teff', 'LOGGADOPN', 'p_el', 'clean', 'petroR90Err_z', 'petroR90Err_r', 'petroR90Err_u', 'ZWARNING', 'resolveStatus', 'petroR90Err_i', 'OBJECT', 'JD', 'nField', 'petroR90Err_g', 'access', 'expMag_g', 'expMag_i', 'expMag_r', 'expMag_u', 'expMag_z', 'ELODIERVFINAL', 'x', 'specObjID', 'metallicity_mean', 'sky_r', 'mE2PSF_i', 'petroR50Err_i', 'sky_u', 'Mi', 'petroR50Err_g', 'mE2PSF_g', 'mE2PSF_z', 'sky_g', 'petroR50Err_z', 'oiii_5007_flux', 'mE2PSF_r', 'petroR50Err_u', 'sky_i', 'petroR50Err_r', 'mE2PSF_u', 'c', 'mCr4_z', 'mCr4_r', 'mCr4_u', 'mCr4_i', 'mCr4_g', 'nObjects', 'modelFluxIvar_z', 'FLAGS_g', 'modelFluxIvar_r', 'tablename', 'modelFluxIvar_u', 'modelFluxIvar_i', 'pa', 'FLAGS_u', 'FLAGS_z', 'modelFluxIvar_g', 'aperFlux7Ivar_u', 'aperFlux7Ivar_r', 'aperFlux7Ivar_z', 'N', 'aperFlux7Ivar_g', 'b_r', 'aperFlux7Ivar_i', 'Flux_OIII_5006', 'raMin', 'PSFMAGERR_g', 'deVPhi_u', 'u_g', 'deVPhi_r', 'u_i', 'deVPhi_z', 'PSFMAGERR_i', 'cModelFluxIvar_z', 'u_r', 'PSFMAGERR_u', 'p_dk', 'PSFMAGERR_r', 'u_u', 'cModelFluxIvar_r', 'u_z', 'PSFMAGERR_z', 'deVPhi_i', 'cModelFluxIvar_u', 'ELODIERVFINALERR', 'stripe', 'regionType', 'flags', 'y', 'sii_6717_flux', 'h_alpha_flux_err', 'parentID', 'z_noqso', 'absMagR', 'bin', 'a_u', 'a_z', 'a_g', 'a_i', 'd', 'p_acw', 'LOGGADOPUNC', 'DEC', 'SpecObjID', 'PSFMAG_r', 'run', 'primTarget', 'PSFMAG_z', 'O', 'PSFMAG_g', 'PSFMAG_i', 'cmax', 'seeing', 'modelMagErr_r', 'modelMagErr_u', 'modelMagErr_z', 'expRad_g', 'modelMagErr_g', 'modelMagErr_i', 'rowv', 'rowc', 'nMgyPerCount_i', 'expFlux_i', 'REDSHIFT', 'expFlux_g', 'nMgyPerCount_g', 'nMgyPerCount_z', 'expFlux_z', 'delta', 'nMgyPerCount_r', 'expFlux_u', 'expFlux_r', 'nMgyPerCount_u', 'nnAvgZ', 'z', 'warning', 'primaryArea', 'T2', 'T1', 'e', 'age', 'Flux_Hb_4861', 'petroMag_i', 'mE1PSF_g', 'mE1PSF_i', 'petroMag_g', 'mE1PSF_r', 'petroMag_z', 'TEFFADOP', 'mE1PSF_u', 'mE1PSF_z', 'petroMag_r', 'CPS', 'petroMag_u', 'mRrCc_r', 'rowvErr', 'viewname', 'mRrCc_z', 'mRrCc_g', 'mRrCc_i', 'RAERR', 'deVRadErr_i', 'deVRadErr_g', 'HUBBLE', 'deVRadErr_z', 'deVRadErr_u', 'deVRadErr_r', 'regionString', 'lnLStar_g', 'lnLStar_i', 'lnLStar_r', 'lnLStar_u', 'survey', 't_age_err', 'f', 'zWarning', 'ALT', 'tau', 'airmass_r', 'airmass_u', 'airmass_z', 'chisq', 'airmass_g', 'airmass_i', 'elliptical', 'PROPERMOTION', 'nnCount', 'CaIIKmask', 'mjd', 'htmid', 'ha', 'regionID', 'age_max', 'lnLExp_z', 'EXTR', 'petroMagErr_g', 'lnLExp_r', 'petroMagErr_i', 'decErr', 'lnLExp_u', 'petroMagErr_r', 'lnLExp_i', 'petroMagErr_u', 'petroMagErr_z', 'lnLExp_g', 'lgm_tot_p50', 'psfWidth_r', 'mode', 'oiii_5007_flux_err', 'apogee_id', 'patch', 's_h', 'w1m', 'Flux_OII_3726', 'g', 'Flux_OII_3728', 'pspStatus', 'vdisp_median', 'pmRaErr', 'date', 'metallicity_err', 'mE1E1Err_g', 'mE1E1Err_i', 'cModelMag_z', 'mE1E1Err_r', 'mE1E1Err_u', 'mE1E1Err_z', 'SEEING', 'ssfr_mean', 'cModelMag_r', 'psfFluxIvar_i', 'psfFluxIvar_z', 'psfFluxIvar_r', 'psfFluxIvar_u', 'fiberMagErr_r', 'fiberMagErr_u', 'fiberMagErr_z', 'plateID', 'fiberMagErr_g', 'fiberMagErr_i', 'fracDeV_g', 'fracDeV_i', 'fracDeV_r', 'fracDeV_u', 'fracDeV_z', 'expRadErr_r', 'expRadErr_g', 'objId', 'expRadErr_i', 'class', 'objID', 'text', 'EXT', 'Flux_Ha_6562', 'FIBERMAG_i', 'petroRad_g', 'petroRad_i', 'nProf_g', 'petroRad_u', 'FLAGS', 'petroRad_r', 'targetObjID', 'nProf_r', 'nProf_u', 'petroRad_z', 'bestObjID', 'photoDec', 'sigma_balmer', 'fiberMag_z', 'mE2E2Err_z', 'fiberMag_r', 'mE2E2Err_r', 'mE2E2Err_u', 'fiberMag_u', 'mE2E2Err_i', 'fiberMag_i', 'psfFlux_u', 'decMax', 'mE2E2Err_g', 'fiberMag_g', 'h_alpha_flux', 'sky_z', 'psfFlux_z', 'covar', 'programName', 'psfMag_r', 'psfMag_u', 'psfMag_z', 'eta', 'psfMag_g', 'psfMag_i', 'skyErr_u', 'cz', 'cy', 'cx', 'Gmask', 'gmr0', 'offsetRa_g', 'offsetRa_i', 'mu', 'offsetRa_r', 'offsetRa_u', 'deVFlux_z', 'offsetRa_z', 'OBJ', 'ssfr_max', 'EXTINCTION_g', 'apstar_id', 'EXTINCTION_z', 'EXTINCTION_r', 'EXTINCTION_u', 'fiberID', 'camcol', 'i', 'probPSF', 'vdisp_err', 'sdss_objid', 'd_u', 'COADD', 'match', 'mjd_r', 'petroRadErr_u', 'petroRadErr_r', 'petroRadErr_z', 'petroRadErr_g', 'petroRadErr_i', 'indexmapid', 'enum', 'd4000_n', 'tiMask', 'FLUXOBJID', 'nii_6584_flux', 'expFluxIvar_i', 'DECERR', 'neiii_3869_flux', 't_age', 'peak', 'FLAGS_r', 'spiral', 'neighborMode', 'PMB', 'PML', 'loadversion', 'chunk', 'hg', 'count', 'lumDist', 'nnVol', 'q_g', 'wise_cntr', 'b_i', 'nDetect', 'qErr_z', 'pid', 'q_i', 'qErr_u', 'q_u', 'q_r', 'thingId', 'q_z', 'mRrCcErr_z', 'mRrCcErr_r', 'vhelio_avg', 'mRrCcErr_u', 'COLC', 'mRrCcErr_i', 'taiBegin', 'metallicity']

parser = ArgumentParser()
parser.add_argument("-f", "--infile", help="Path to input file")
parser.add_argument("-s", "--suffix", help="output suffix, with dot")
args = parser.parse_args()

# if len(args.infile) == 0 or len(args.outfile) == 0:
	# print 'Incorrect usage: Both --infile and --outfile are required.'
	# sys.exit(1)


INFILENAME = args.infile
OUTFILENAME = args.infile+args.suffix

sdss_tables_views = sdss_tables + sdss_views

# table_patterns = map(lambda t: (t.lower(), re.compile(" "+t+" ", re.IGNORECASE), re.compile(" "+t+"\.", re.IGNORECASE)), sdss_tables_views)
# column_patterns = map(lambda c: (c.lower(), re.compile(" "+c+" ", re.IGNORECASE), re.compile("\."+c+" ", re.IGNORECASE)), sdss_columns)
# func_patterns = map(lambda f: (f.lower(), re.compile(" "+f+" \(", re.IGNORECASE), re.compile("\."+f+" \(", re.IGNORECASE)), sdss_functions)

quoted_patterns = map(lambda q: (q.lower(), re.compile(q, re.IGNORECASE)), quoted+unknown)

def format_tables(line):
	for table, pattern_space, pattern_dot in table_patterns:
		line = pattern_space.sub(" "+table+" ", line)
		line = pattern_dot.sub(" "+table+".", line)
	return line

def format_columns(line):
	for col, pattern_space, pattern_dot in column_patterns:
		line = pattern_space.sub(" "+col+" ", line)
		line = pattern_dot.sub("."+col+" ", line)
	return line

def format_functions(line):
	for func, pattern_space, pattern_dot in func_patterns:
		line = pattern_space.sub(" "+func+" (", line)
		line = pattern_dot.sub("."+func+" (", line)
	return line

def format_alias(line):
	p = re.compile(" [A-Z] ")
	matches = re.findall(p,line)
	for matched_alias in matches:
		alias = matched_alias.strip()
		pattern_aliasdef = re.compile(matched_alias)
		pattern_aliascol = re.compile(" "+alias+"\.")
		line = pattern_aliasdef.sub(matched_alias.lower(), line)
		line = pattern_aliascol.sub(" "+alias.lower()+".", line)
	return line

def format_tab(line):
	line = re.sub("\t", " ", line)
	line = re.sub(" +", " ", line)
	return line

def format_quoted(line):
	for quoted, pattern in quoted_patterns:
		line = pattern.sub(quoted, line)
	return line


def purge_imbalanced(line):
	tokens = line.split()
	num_open = len(filter(lambda x: x=="(", tokens))
	num_close = len(filter(lambda x: x==")", tokens))
	if num_open == num_close:
		return line
	else:
		return None


def filter_unks(line):
	max_unks_per_line = 19.32
	tokens = line.split()
	unkcount = len(filter(lambda x: x=="<UNK>", tokens))
	p = 100.0 * unkcount / len(tokens)
	if p < max_unks_per_line:
		return line
	else:
		return None

operator_prefix = "(<|>|<=|>=|<>|!=|=)"
# Replace the following patterns with <VAL> or <ARG>
# 0x112d0a6661da0000 (fieldId, specObjId, objid)
hex_pattern = re.compile(operator_prefix+" 0x[0-9a-f]{3,} ", re.IGNORECASE)
# 456084050738702336 (specObjId) long_int18 = re.compile("[0-9]{18}")
int_pattern = re.compile(operator_prefix+" \-?[0-9]{3,} ")
# 169.0114773027, 57.36489549890447 (p.dec), 0.28900000 (h.z), 194.6
dec_pattern = re.compile(operator_prefix+" \-?[0-9]+\.[0-9]{2,} ")
unk_pattern = re.compile(operator_prefix+" <UNK> ")
# btn_pattern = re.compile("BETWEEN \-?([0-9]{3,}|[0-9]+\.[0-9]{2,}|<UNK>) AND \-?([0-9]{3,}|[0-9]+\.[0-9]{2,}|<UNK>) ")
btn_pattern = re.compile("BETWEEN \-?([0-9]{3,}|[0-9]+\.[0-9]+|<UNK>) AND \-?([0-9]{3,}|[0-9]+\.[0-9]+|<UNK>) ")
btn_unk_pattern1 = re.compile("BETWEEN <UNK> AND")
btn_unk_pattern2 = re.compile("(BETWEEN (\-?\d*(\.\d+)?|<VAL>) AND) <UNK> ")
val_replacement = r'\1 <VAL> '

def replace_val(line):
	line = re.sub(hex_pattern, val_replacement, line)
	line = re.sub(int_pattern, val_replacement, line)
	line = re.sub(dec_pattern, val_replacement, line)
	line = re.sub(unk_pattern, val_replacement, line)
	line = re.sub(btn_pattern, "BETWEEN <VAL> AND <VAL> ", line)
	line = re.sub(btn_unk_pattern1, "BETWEEN <VAL> AND", line)
	line = re.sub(btn_unk_pattern2, val_replacement, line)
	return line


arg_pattern = re.compile("(\(|,) \-?([0-9]+\.[0-9]{2,}|[0-9]{2,}\.[0-9]+) (\)|,)")
arg_replacement = r'\1 <ARG> \3'
hexarg_pattern = re.compile("(\(|,) 0x[0-9a-f]{3,}")
intarg_pattern = re.compile("(\(|,) [0-9]{10,}")
numarg_replacement = r'\1 <ARG>'
def replace_arg(line):
	line = re.sub(hexarg_pattern, numarg_replacement, line)
	line = re.sub(intarg_pattern, numarg_replacement, line)
	while True:
		r=re.sub(arg_pattern, arg_replacement, line)
		if r==line:
			return unk2arg(r)
		else:
			line = r

unk_arg1_pattern = re.compile("\( <UNK>")
unk_arg1_replacement = "( <ARG>"
unk_arg2_pattern = re.compile("<ARG> , <UNK>")
unk_arg2_replacement = "<ARG> , <ARG>"
def unk2arg(line):
	line = re.sub(unk_arg1_pattern, unk_arg1_replacement, line)
	while True:
		r=re.sub(unk_arg2_pattern, unk_arg2_replacement, line)
		if r==line:
			return line
		else:
			line = r


output = subprocess.check_output("wc -l %s" % INFILENAME, shell=True)
numlines = output.split()[0]

with open(INFILENAME) as in_file:
	with open(OUTFILENAME, 'w') as out_file:
		chkpt = 0
		last_chkpt = 0
		for line in in_file:
			# line = purge_imbalanced(line)
			# line = filter_unks(line)
			line = replace_val(line)
			line = replace_arg(line)

			if line is None:
				continue

			out_file.write(line)
			
			# line = format_tables(line)
			# line = format_columns(line)
			# line = format_functions(line)
			# line = format_alias(line)
			# line = format_quoted(line)
			# line = format_tab(line)
			# for w in line.split():
				# if w.upper() in keywords_to_case:
					# line = line.replace(w, w.upper())
				# line = line.replace(func.lower()+' (', func+' (')
				# line = line.replace(k, ' '+k+' ')
			chkpt += 1
			if chkpt - last_chkpt == 1000:
				last_chkpt = chkpt
				# print(chkpt)
				stdout.write("\r%d/%s lines processed" % (chkpt, numlines))
				stdout.flush()
stdout.write("\n")


