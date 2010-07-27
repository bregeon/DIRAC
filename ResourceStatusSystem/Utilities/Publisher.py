########################################################################
# $HeadURL:  $
########################################################################

__RCSID__ = "$Id:  $"

import copy
import threading

from DIRAC.ResourceStatusSystem.Utilities.Utils import *
from DIRAC.ResourceStatusSystem.Utilities.Exceptions import *
from DIRAC.Core.Utilities.ThreadPool import ThreadPool

from DIRAC.ResourceStatusSystem.Utilities.CS import *

class Publisher:
  """ 
  Class Publisher is in charge of getting dispersed information, to be published on the web.
  """

#############################################################################

  def __init__(self, VOExtension, rsDBIn = None, commandCallerIn = None, infoGetterIn = None, 
               WMSAdminIn = None):
    """ 
    Standard constructor
    
    :params:
      :attr:`VOExtension`: string, VO Extension (e.g. 'LHCb')

      :attr:`rsDBIn`: optional ResourceStatusDB object 
      (see :class: `DIRAC.ResourceStatusSystem.DB.ResourceStatusDB.ResourceStatusDB`)
    
      :attr:`commandCallerIn`: optional CommandCaller object
      (see :class: `DIRAC.ResourceStatusSystem.Command.CommandCaller.CommandCaller`) 
    
      :attr:`infoGetterIn`: optional InfoGetter object
      (see :class: `DIRAC.ResourceStatusSystem.Utilities.InfoGetter.InfoGetter`) 
    
      :attr:`WMSAdminIn`: optional RPCClient object for WMSAdmin
      (see :class: `DIRAC.Core.DISET.RPCClient.RPCClient`) 
    """
    
    self.configModule = __import__(VOExtension+"DIRAC.ResourceStatusSystem.Policy.Configurations", 
                                   globals(), locals(), ['*'])
    
    if rsDBIn is not None:
      self.rsDB = rsDBIn
    else:
      from DIRAC.ResourceStatusSystem.DB.ResourceStatusDB import ResourceStatusDB
      self.rsDB = ResourceStatusDB()
    
    if commandCallerIn is not None:
      self.cc = commandCallerIn
    else:
      from DIRAC.ResourceStatusSystem.Command.CommandCaller import CommandCaller
      self.cc = CommandCaller() 
    
    if infoGetterIn is not None:
      self.ig = infoGetterIn
    else:
      from DIRAC.ResourceStatusSystem.Utilities.InfoGetter import InfoGetter
      self.ig = InfoGetter(VOExtension)
    
    if WMSAdminIn is not None:
      self.WMSAdmin = WMSAdminIn
    else:
      from DIRAC.Core.DISET.RPCClient import RPCClient
      self.WMSAdmin = RPCClient("WorkloadManagement/WMSAdministrator")
    
    self.threadPool = ThreadPool( 2, 5 )
    
    self.lockObj = threading.RLock()

    self.infoForPanel_res = {}

#############################################################################

  def getInfo(self, granularity, name, useNewRes = False):
    """ 
    Standard method to get all the info to be published
    
    This method uses a ThreadPool (:class:`DIRAC.Core.Utilities.ThreadPool.ThreadPool`)
    with 2-5 threads. The threaded method is 
    :meth:`DIRAC.ResourceStatusSystem.Utilities.Publisher.Publisher.getInfoForPanel`
    
    :params:
      :attr:`granularity`: string - a ValidRes 
      
      :attr:`name`: string - name of the Validres
      
      :attr:`useNewRes`: boolean. When set to true, will get new results, 
      otherwise it will get cached results (where available).
    """
    
    if granularity not in ValidRes:
      raise InvalidRes, where(self, self.getInfo)

    self.infoForPanel_res = {}

    resType = None
    if granularity in ('Resource', 'Resources'):
      try:
        resType = self.rsDB.getMonitoredsList('Resource', ['ResourceType'], 
                                              resourceName = name)[0][0]
      except IndexError:
        return "%s does not exist!" %name
                                            
    paramNames = ['Type', 'Group', 'Name', 'Policy', 'DIRAC Status',
                  'RSS Status', 'Reason', 'Description']
    
    infoToGet = self.ig.getInfoToApply(('view_info', ), granularity, None, None, 
                                       None, None, resType, useNewRes)[0]['Panels']
    
    infoToGet_res = {}
    
    recordsList = []

    for panel in infoToGet.keys():
      
      (granularityForPanel, nameForPanel) = self.__getNameForPanel(granularity, name, panel)
      
      if not self._resExist(granularityForPanel, nameForPanel):
        completeInfoForPanel_res = None
        continue
      
      #take composite RSS result for name
      nameStatus_res = self._getStatus(nameForPanel, panel)
      
      recordBase = [None, None, None, None, None, None, None, None]
      infosForPolicy = {}
      
      recordBase[1] = panel.replace('_Panel', '')
      recordBase[2] = nameForPanel #nameForPanel
      try:
        recordBase[4] = nameStatus_res[nameForPanel]['DIRACStatus'] #DIRAC Status
      except:
        pass
      recordBase[5] = nameStatus_res[nameForPanel]['RSSStatus'] #RSS Status
      
      record = copy.deepcopy(recordBase)
      record[0] = 'ResultsForResource'
      
      recordsList.append(record)
      
      #take info that goes into the panel
      infoForPanel = infoToGet[panel]
      
      for info in infoForPanel:
        
        self.threadPool.generateJobAndQueueIt(self.getInfoForPanel, 
                                              args = (info, granularityForPanel, nameForPanel) )

      self.threadPool.processAllResults()

      for policy in self.infoForPanel_res.keys():
        record = copy.deepcopy(recordBase)
        record[0] = 'SpecificInformation'
        record[3] = policy #policyName
        record[4] = None #DIRAC Status
        record[5] = self.infoForPanel_res[policy]['Status'] #RSS status for the policy
        record[6] = self.infoForPanel_res[policy]['Reason'] #Reason
        record[7] = self.infoForPanel_res[policy]['desc'] #Description
        recordsList.append(record)
        
        infosForPolicy[policy] = self.infoForPanel_res[policy]['infos']
        
      infoToGet_res['TotalRecords'] = len(recordsList)
      infoToGet_res['ParameterNames'] = paramNames
      infoToGet_res['Records'] = recordsList
  
      infoToGet_res['Extras'] = infosForPolicy

    return infoToGet_res

#############################################################################

  def getInfoForPanel(self, info, granularityForPanel, nameForPanel):

    #get single RSS policy results
    policyResToGet = info.keys()[0]
    pol_res = self.rsDB.getPolicyRes(nameForPanel, policyResToGet)
    if pol_res != []:
      pol_res_dict = {'Status' : pol_res[0], 'Reason' : pol_res[1]}
    else:
      pol_res_dict = {'Status' : 'Unknown', 'Reason' : 'Unknown'}
    self.lockObj.acquire()
    try:
      self.infoForPanel_res[policyResToGet] = pol_res_dict
    finally:
      self.lockObj.release()
    
    #get policy description
    desc = self._getPolicyDesc(policyResToGet)
    
    #get other info
    othersInfo = info.values()[0]
    if not isinstance(othersInfo, list):
      othersInfo = [othersInfo]
    
    info_res = {}
    
    for oi in othersInfo:
      format = oi.keys()[0]
      what = oi.values()[0]
      
      info_bit_got = self._getInfo(granularityForPanel, nameForPanel, format, what)
                
      info_res[format] = info_bit_got
      
    self.lockObj.acquire()
    try:
      self.infoForPanel_res[policyResToGet]['infos'] = info_res 
      self.infoForPanel_res[policyResToGet]['desc'] = desc
    finally:
      self.lockObj.release()

#############################################################################
  
  def _getStatus(self, name, panel):
  
    #get RSS status
    RSSStatus = self._getInfoFromRSSDB(name, panel)[0][1]
    
    #get DIRAC status
    if panel in ('Site_Panel', 'SE_Panel'):
      
      if panel == 'Site_Panel':
        DIRACStatus = self.WMSAdmin.getSiteMaskLogging(name)
        if DIRACStatus['OK']:
          DIRACStatus = DIRACStatus['Value'][name].pop()[0]
        else:
          raise RSSException, where(self, self._getStatus)
      
      elif panel == 'SE_Panel':
        ra = getStorageElementStatus(name, 'ReadAccess')['Value']
        wa = getStorageElementStatus(name, 'WriteAccess')['Value']
        DIRACStatus = {'ReadAccess': ra, 'WriteAccess': wa}
      
      status = { name : { 'RSSStatus': RSSStatus, 'DIRACStatus': DIRACStatus } }

    else:
      status = { name : { 'RSSStatus': RSSStatus} }
      
    
    return status

#############################################################################

  def _getInfo(self, granularity, name, format, what):
  
    if format == 'RSS':
      info_bit_got = self._getInfoFromRSSDB(name, what)
    else:
      if isinstance(what, dict):
        command = what['CommandIn']
        extraArgs = what['args']
      else:
        command = what
        extraArgs = None
      
      info_bit_got = self.cc.commandInvocation(granularity, name, None, 
                                               None, command, extraArgs)

    return info_bit_got

#############################################################################

  def _getInfoFromRSSDB(self, name, what):

    paramsL = ['Status']

    siteName = None
    serviceName = None
    resourceName = None
    storageElementName = None
    
    if what == 'ServiceOfSite':
      gran = 'Service'
      paramsL.insert(0, 'ServiceName')
      paramsL.append('Reason')
      siteName = name
    elif what == 'ResOfCompService':
      gran = 'Resources'
      paramsL.insert(0, 'ResourceName')
      paramsL.append('Reason')
      serviceName = name
    elif what == 'ResOfStorService':
      gran = 'Resources'
      paramsL.insert(0, 'ResourceName')
      paramsL.append('Reason')
      serviceName = name
    elif what == 'ResOfStorEl':
      gran = 'StorageElements'
      paramsL.insert(0, 'ResourceName')
      paramsL.append('Reason')
      storageElementName = name
    elif what == 'StorageElementsOfSite':
      gran = 'StorageElements'
      paramsL.insert(0, 'StorageElementName')
      paramsL.append('Reason')
      if '@' in name:
        siteName = name.split('@').pop()
      else:
        siteName = name
    elif what == 'Site_Panel':
      gran = 'Site'
      paramsL.insert(0, 'SiteName')
      siteName = name
    elif what == 'Service_Computing_Panel':
      gran = 'Service'
      paramsL.insert(0, 'ServiceName')
      serviceName = name
    elif what == 'Service_Storage_Panel':
      gran = 'Service'
      paramsL.insert(0, 'ServiceName')
      serviceName = name
    elif what == 'Service_VO-BOX_Panel':
      gran = 'Services'
      paramsL.insert(0, 'ServiceName')
      serviceName = name
    elif what == 'Service_VOMS_Panel':
      gran = 'Services'
      paramsL.insert(0, 'ServiceName')
      serviceName = name
    elif what == 'Resource_Panel':
      gran = 'Resource'
      paramsL.insert(0, 'ResourceName')
      resourceName = name
    elif what == 'SE_Panel':
      gran = 'StorageElement'
      paramsL.insert(0, 'StorageElementName')
      storageElementName = name
      
    info_bit_got = self.rsDB.getMonitoredsList(gran, paramsList = paramsL, siteName = siteName, 
                                               serviceName = serviceName, resourceName = resourceName,
                                               storageElementName = storageElementName)
    
    return info_bit_got

#############################################################################

  def _getPolicyDesc(self, policyName):
    
    return self.configModule.Policies[policyName]['Description']

#############################################################################

  def __getNameForPanel(self, granularity, name, panel):

    if granularity in ('Site', 'Sites'):
      if panel == 'Service_Computing_Panel':
        granularity = 'Service'
        name = 'Computing@' + name
      elif panel == 'Service_Storage_Panel':
        granularity = 'Service'
        name = 'Storage@' + name
      elif panel == 'OtherServices_Panel':
        granularity = 'Service'
        name = 'OtherS@' + name
      elif panel == 'Service_VOMS_Panel':
        granularity = 'Service'
        name = 'VOMS@' + name
      elif panel == 'Service_VO-BOX_Panel':
        granularity = 'Service'
        name = 'VO-BOX@' + name
#      else:
#        granularity = granularity
#        name = name
#    else:
#      granularity = granularity
#      name = name
      
    return (granularity, name)

#############################################################################

  def _resExist(self, granularity, name):
    
    siteName = None
    serviceName = None
    resourceName = None
    storageElementName = None
    
    if granularity in ('Site', 'Sites'):
      siteName = name
    elif granularity in ('Service', 'Services'):
      serviceName = name
    elif granularity in ('Resource', 'Resources'):
      resourceName = name
    elif granularity in ('StorageElement', 'StorageElements'):
      storageElementName = name
    
    res = self.rsDB.getMonitoredsList(granularity, siteName = siteName, 
                                      serviceName = serviceName, resourceName = resourceName,
                                      storageElementName = storageElementName)
    
    if res == []:
      return False
    else: 
      return True
    
#############################################################################
