# Install script for directory: /mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2

# Set the install prefix
IF(NOT DEFINED CMAKE_INSTALL_PREFIX)
  SET(CMAKE_INSTALL_PREFIX "/usr/local")
ENDIF(NOT DEFINED CMAKE_INSTALL_PREFIX)
STRING(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
IF(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  IF(BUILD_TYPE)
    STRING(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  ELSE(BUILD_TYPE)
    SET(CMAKE_INSTALL_CONFIG_NAME "")
  ENDIF(BUILD_TYPE)
  MESSAGE(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
ENDIF(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)

# Set the component getting installed.
IF(NOT CMAKE_INSTALL_COMPONENT)
  IF(COMPONENT)
    MESSAGE(STATUS "Install component: \"${COMPONENT}\"")
    SET(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  ELSE(COMPONENT)
    SET(CMAKE_INSTALL_COMPONENT)
  ENDIF(COMPONENT)
ENDIF(NOT CMAKE_INSTALL_COMPONENT)

# Install shared libraries without execute permission?
IF(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  SET(CMAKE_INSTALL_SO_NO_EXE "0")
ENDIF(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/build/lib/libredis++.a")
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  IF(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libredis++.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libredis++.so")
    FILE(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libredis++.so"
         RPATH "")
  ENDIF()
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/build/libredis++.so")
  IF(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libredis++.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libredis++.so")
    FILE(RPATH_REMOVE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libredis++.so")
    IF(CMAKE_INSTALL_DO_STRIP)
      EXECUTE_PROCESS(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libredis++.so")
    ENDIF(CMAKE_INSTALL_DO_STRIP)
  ENDIF()
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/usr/local/include/sw/redis++/connection.h;/usr/local/include/sw/redis++/reply.h;/usr/local/include/sw/redis++/command_options.h;/usr/local/include/sw/redis++/utils.h;/usr/local/include/sw/redis++/redis.h;/usr/local/include/sw/redis++/queued_redis.h;/usr/local/include/sw/redis++/config.h;/usr/local/include/sw/redis++/queued_redis.hpp;/usr/local/include/sw/redis++/errors.h;/usr/local/include/sw/redis++/command_args.h;/usr/local/include/sw/redis++/redis++.h;/usr/local/include/sw/redis++/redis_cluster.hpp;/usr/local/include/sw/redis++/shards_pool.h;/usr/local/include/sw/redis++/subscriber.h;/usr/local/include/sw/redis++/redis.hpp;/usr/local/include/sw/redis++/pipeline.h;/usr/local/include/sw/redis++/redis_cluster.h;/usr/local/include/sw/redis++/connection_pool.h;/usr/local/include/sw/redis++/command.h;/usr/local/include/sw/redis++/shards.h;/usr/local/include/sw/redis++/transaction.h")
  IF (CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  ENDIF (CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
  IF (CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  ENDIF (CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
FILE(INSTALL DESTINATION "/usr/local/include/sw/redis++" TYPE FILE FILES
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/connection.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/reply.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/command_options.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/utils.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/redis.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/queued_redis.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/config.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/queued_redis.hpp"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/errors.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/command_args.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/redis++.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/redis_cluster.hpp"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/shards_pool.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/subscriber.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/redis.hpp"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/pipeline.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/redis_cluster.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/connection_pool.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/command.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/shards.h"
    "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/src/sw/redis++/transaction.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")

IF(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  INCLUDE("/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/build/test/cmake_install.cmake")

ENDIF(NOT CMAKE_INSTALL_LOCAL_ONLY)

IF(CMAKE_INSTALL_COMPONENT)
  SET(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
ELSE(CMAKE_INSTALL_COMPONENT)
  SET(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
ENDIF(CMAKE_INSTALL_COMPONENT)

FILE(WRITE "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/build/${CMAKE_INSTALL_MANIFEST}" "")
FOREACH(file ${CMAKE_INSTALL_MANIFEST_FILES})
  FILE(APPEND "/mnt/hgfs/Projects/SmartHome/Branches/GreenHomeProxyCXX/opensource/redis-plus-plus-1.0.2/build/${CMAKE_INSTALL_MANIFEST}" "${file}\n")
ENDFOREACH(file)
