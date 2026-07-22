//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : MarketProvider.mqh                                     |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_PROVIDER_MQH
#define CORE_MARKET_PROVIDER_MQH

#include "../MarketData.mqh"
#include "../Engine/MarketEngine.mqh"

class CMarketProvider
{
private:

   CMarketData   m_data;
   CMarketEngine m_engine;

public:

   bool Initialize()
   {
      return true;
   }

   void Update()
   {
   }

   CMarketData Data()
   {
      return m_data;
   }

   CMarketEngine Engine()
   {
      return m_engine;
   }
};

#endif