//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : MarketManager.mqh                                      |
//| Layer   : Market / Providers                                     |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_PROVIDERS_MARKETMANAGER_MQH
#define CORE_MARKET_PROVIDERS_MARKETMANAGER_MQH

#include "MarketProvider.mqh"

class CMarketManager
{
private:

   CMarketProvider m_provider;

public:

   bool Initialize()
   {
      return m_provider.Initialize();
   }

   void Update()
   {
      m_provider.Update();
   }

   CMarketData Data()
   {
      return m_provider.Data();
   }

   CMarketEngine Engine()
   {
      return m_provider.Engine();
   }

};

#endif