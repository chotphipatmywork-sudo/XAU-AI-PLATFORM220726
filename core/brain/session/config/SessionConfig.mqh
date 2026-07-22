//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SessionConfig.mqh                                      |
//| Layer   : Brain / Session / Config                               |
//| Version : 1.0.0                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_SESSION_CONFIG_SESSIONCONFIG_MQH
#define CORE_BRAIN_SESSION_CONFIG_SESSIONCONFIG_MQH

class CSessionConfig
{
public:

   bool EnableAsia;

   bool EnableLondon;

   bool EnableNewYork;

   CSessionConfig()
   {
      EnableAsia = true;

      EnableLondon = true;

      EnableNewYork = true;
   }
};

#endif