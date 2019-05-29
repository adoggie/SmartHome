//
// Created by scott on 2019-03-12.
//

#ifndef INNERPROC_UTILS_H
#define INNERPROC_UTILS_H

#include <string>
#include <string>
#include <sstream>
#include <vector>


namespace utils {
    std::string generateUUID();
    std::string getIpAddress(const std::string& eth="eth0");

    typedef std::vector<std::uint8_t > ByteArray;
    int fromHex( char c ) ;
    std::uint8_t fromHex( const char *c ) ;
    ByteArray convertHex2Bin(const char* data,size_t size);
    std::string toHex(const void* inRaw, int len);
    std::string toHexLower(const void* inRaw, int len) ;


    std::string generateSignature(const std::string& secret_key,const std::string& text);

    std::string getDeviceUniqueId();
    bool writeDeviceUniqueId(const std::string& uid);

    //设置网卡地址
    bool setNicIpAddress(const std::string& nic,const std::string& ip );
}

#endif //INNERPROC_UTILS_H
