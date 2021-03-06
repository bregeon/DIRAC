# FIXME: should be re-written using real unittest

# #!/usr/bin/env python
# """
# """
#
# __RCSID__ = "$Id$"
#
# import DIRAC
# import tempfile
# import os
# import time
#
# from DIRAC import gLogger
# gLogger.setLevel( 'DEBUG' )
#
# DIRAC.gLogger.initialize('test_Utilities','/testSection')
#
# testList = [{ 'method'    : DIRAC.List.uniqueElements,
#               'arguments' : ( ( 1, 2, 3, 4, 5, 1 ), ),
#               'output'    : [ 1, 2, 3, 4, 5 ]
#             },
#             { 'method'    : DIRAC.List.uniqueElements,
#               'arguments' : ( [ 1, 2, 3, 4, 5, 1 ], ),
#               'output'    : [ 1, 2, 3, 4, 5 ]
#             },
#             { 'method'    : DIRAC.List.uniqueElements,
#               'arguments' : ( { 1 : 1, 2 : 2, 3 : 3, 4 : 4, 2 : 5, 5 : 6 }, ),
#               'output'    : [ 1, 2, 3, 4, 5 ]
#             },
#             { 'method'    : DIRAC.List.fromChar,
#               'arguments' : ( '/one/two/','/' ),
#               'output'    : [ 'one','two' ]
#             },
#             { 'method'    : DIRAC.List.fromChar,
#               'arguments' : ( '/one/two/','' ),
#               'output'    : None
#             },]
#
# inPath  = '/mypath:/yourpath:/mypath:/hispath'
# outPath = '/mypath:/yourpath:/hispath'
# testOs = [{ 'method'    : DIRAC.Os.uniquePath,
#             'arguments' : ( inPath, ),
#             'output'    : outPath
#                        },]
#
# tmpFd, tmpName = tempfile.mkstemp()
# tmpFile = os.fdopen( tmpFd, 'w' )
# tmpFile.write( 'This is test file for md5 checksum test' )
# tmpFile.close()
# testFile = [{ 'method'    : DIRAC.File.makeGuid,
#               'arguments' : ( tmpName, ),
#               'output'    : '131090BF-5445-2EB3-6606-B96A75B287A6'
#             },]
#
# def testTime():
#
#   curDateTime = DIRAC.Time.dateTime()
#   curDate     = DIRAC.Time.date( curDateTime )
#   curTime     = DIRAC.Time.time( curDateTime )
#   curDateTimeString = DIRAC.Time.toString( curDateTime )
#   curDateString     = DIRAC.Time.toString( curDate )
#   curTimeString     = DIRAC.Time.toString( curTime )
#
#   newDateTimeString = curDateString + " " + curTimeString
#
#   interval    = DIRAC.Time.timeInterval( curDateTime, curTime )
#   inDateTime  = curDateTime + curTime / 2
#   outDateTime = curDateTime + curTime * 2
#
#   testToString = [{ 'method'    : DIRAC.Time.toString,
#                     'arguments' : ( curDateTime, ),
#                     'output'    : newDateTimeString
#                   },]
#
#   testFromString1 = [{ 'method'    : DIRAC.Time.fromString,
#                        'arguments' : ( curDateTimeString, ),
#                        'output'    : curDateTime
#                      },]
#
#   testFromString2 = [{ 'method'    : DIRAC.Time.fromString,
#                        'arguments' : ( curDateString, ),
#                        'output'    : curDate
#                      },]
#
#   testFromString3 = [{ 'method'    : DIRAC.Time.fromString,
#                        'arguments' : ( curTimeString, ),
#                        'output'    : curTime
#                      },]
#
#   testInInterval  = [{ 'method'    : interval.includes,
#                        'arguments' : ( inDateTime, ),
#                        'output'    : True
#                      },]
#
#   testOutInterval  = [{ 'method'    : interval.includes,
#                         'arguments' : ( outDateTime, ),
#                         'output'    : False
#                      },]
#
#
#   testdict = { 'DIRAC.Time.timeToString'               : testToString,
#                'DIRAC.Time.timeFromString( DateTime )' : testFromString1,
#                'DIRAC.Time.timeFromString( Date )'     : testFromString2,
#                'DIRAC.Time.timeFromString( Time )'     : testFromString3,
#                'DIRAC.Time.timeInterval( In )'     : testInInterval,
#                'DIRAC.Time.timeInterval( Out )'    : testOutInterval }
#
# #   DIRAC.Tests.run( testdict )
#
#   return True
#
# def testNetwork():
#
#   testAllInterfaces = [{ 'method'    : DIRAC.Network.getAllInterfaces,
#                          'arguments' : ( ),
#                          'output'    : False
#                        }, ]
#
#   testAddressFromInterface = [{ 'method'    : DIRAC.Network.getAddressFromInterface,
#                                 'arguments' : ( 'lo', ),
#                                 'output'    : '127.0.0.1'
#                               }, ]
#
#
#   testdict = { 'DIRAC.Network.getAllInterfaces'        : testAllInterfaces,
#                'DIRAC.Network.getAddressFromInterface' : testAddressFromInterface }
#
#   testdict = { 'DIRAC.Network.getAddressFromInterface' : testAddressFromInterface }
#
# #   DIRAC.Tests.run( testdict )
#   return True
#
# def writeToStdout( iIndex, sLine ):
#   if iIndex == 0: # stdout
#     DIRAC.gLogger.info( 'stdout:', sLine )
#   if iIndex == 1: # stderr
#     DIRAC.gLogger.error( 'stderr:', sLine )
#
# def failingWriteToStdOut( iIndex ):
#   pass
#
#
# # def testSubprocess():
# #
# #   testShellCall = [{ 'method'    : DIRAC.shellCall,
# #                      'arguments' : ( 5, 'echo 10', writeToStdout ),
# #                      'output'    : {'OK': True, 'Value': (0, '10\n', '')}
# #                    },
# #                    { 'method'    : DIRAC.shellCall,
# #                      'arguments' : ( 5, 'echo 10 1>&2', writeToStdout ),
# #                      'output'    : {'OK': True, 'Value': (0, '', '10\n')}
# #                    },
# #                    { 'method'    : DIRAC.shellCall,
# #                      'arguments' : ( 5, 'echo $TIME', None, { 'TIME' : '10' } ),
# #                      'output'    : {'OK': True, 'Value': (0, '10\n', '')}
# #                    },
# #                    { 'method'    : DIRAC.shellCall,
# #                      'arguments' : ( 5, ['echo 10'] ),
# #                      'output'    : {'OK': True, 'Value': (0, '10\n', '')}
# #                    },
# #                    { 'method'    : DIRAC.shellCall,
# #                      'arguments' : ( 5, ['echo 10'], failingWriteToStdOut ),
# #                      'output'    : {'OK': True, 'Value': (0, '10\n', '')}
# #                    },
# #                    { 'method'    : DIRAC.shellCall,
# #                      'arguments' : ( 5, 'echo 10 && sleep 10' ),
# #                      'output'    : {'Message': "Timeout (5 seconds) for 'echo 10 && sleep 10' call",
# #                                     'OK': False,
# #                                     'Value': (-9, '10\n', '')}
# #                    }]
# #
# #   testSystemCall = [{ 'method'    : DIRAC.systemCall,
# #                       'arguments' : ( 3, ['/bin/echo', '$TIME'], writeToStdout, {'PATH':'/bin','TIME': '10'} ),
# #                       'output'    : { 'OK': True, 'Value': (0, '$TIME\n', '')}
# #                     },
# #                     { 'method'    : DIRAC.systemCall,
# #                       'arguments' : ( 3, ['/usr/bin/printenv', 'TIME'], writeToStdout, {'TIME': '10'} ),
# #                       'output'    : { 'OK': True, 'Value': (0, '10\n', '')}
# #                     },
# #                     { 'method'    : DIRAC.systemCall,
# #                       'arguments' : ( 3, ['sleep', '10'], writeToStdout, {'PATH':'/bin'} ),
# #                       'output'    : {'Message': "Timeout (3 seconds) for '['sleep', '10']' call",
# #                                      'OK': False,
# #                                      'Value': (-9, '', '')}
# #                     }, ]
# #   testPythonCall = [{ 'method'    : DIRAC.pythonCall,
# #                       'arguments' : ( 3, time.sleep, 5 ),
# #                       'output'    : {'Message': '3 seconds timeout for "sleep" call', 'OK': False}
# #                     },
# #                     { 'method'    : DIRAC.pythonCall,
# #                       'arguments' : ( 5, time.sleep, 3 ),
# #                       'output'    : {'OK': True, 'Value': None}
# #                     },]
# #
# #   testdict = { 'DIRAC.systemCall' : testSystemCall,
# #                'DIRAC.shellCall'  : testShellCall,
# #                'DIRAC.pythonCall' : testPythonCall }
# #
# #   DIRAC.Tests.run( testdict )
# #
# #   return True
#
# testTime = [{ 'method'    : testTime,
#               'arguments' : ( ),
#               'output'    : True
#             },]
#
# testNetwork = [{ 'method'    : testNetwork,
#                  'arguments' : ( ),
#                  'output'    : True
#                },]
#
# testReturnValues = [{ 'method'    : DIRAC.ReturnValues.S_OK,
#                       'arguments' : ( 24, ),
#                       'output'    : { 'OK': 1, 'Value': 24}
#                     },
#                     { 'method'    : DIRAC.ReturnValues.S_ERROR,
#                       'arguments' : ( 24, ),
#                       'output'    : { 'OK': 0, 'Message': '24'}
#                     },]
#
# # testSubprocess = [ { 'method'    : testSubprocess,
# #                      'arguments' : ( ),
# #                       'output'    : True
# #                    },]
#
#
# testdict = { 'DIRAC.List'               : testList,
#              'DIRAC.Os'                 : testOs,
#              'DIRAC.File'               : testFile,
#              'DIRAC.Time'               : testTime,
# #             'DIRAC.Network'            : testNetwork,
#              'DIRAC.ReturnValues'       : testReturnValues,
# #              'DIRAC.SubprocessExecuter' : testSubprocess,
#             }
#
# DIRAC.Tests.run( testdict, 'DIRAC.Utilities' )
# os.remove( tmpName )
#
# DIRAC.exit()
