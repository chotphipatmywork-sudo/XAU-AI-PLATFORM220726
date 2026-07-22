//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : EMAProvider.mqh                                        |
//| Layer   : Indicators / Providers                                 |
//| Version : 2.0.1                                                  |
//| Purpose : EMA Provider (Real MT5 Implementation)                 |
//+------------------------------------------------------------------+

#ifndef CORE_INDICATORS_PROVIDERS_EMAPROVIDER_MQH
#define CORE_INDICATORS_PROVIDERS_EMAPROVIDER_MQH

#include "../models/IndicatorContext.mqh"

//--------------------------------------------------

class CEMAProvider
{
private:

   CIndicatorContext m_context;

public:

   CEMAProvider()
   {
   }

   //--------------------------------------------------

   void SetContext(const CIndicatorContext &context)
   {
      m_context = context;
   }

   //--------------------------------------------------

   double GetValue(
      const int period,
      const int shift = 0)
   {
      int handle =
         iMA(
            m_context.Symbol,
            m_context.Timeframe,
            period,
            0,
            MODE_EMA,
            PRICE_CLOSE);

      if(handle == INVALID_HANDLE)
         return 0.0;

      double buffer[];

      if(CopyBuffer(handle,0,shift,1,buffer) <= 0)
      {
         IndicatorRelease(handle);
         return 0.0;
      }

      IndicatorRelease(handle);

      return buffer[0];
   }

   //--------------------------------------------------

   bool Update()
   {
      return true;
   }

   //--------------------------------------------------

   void Reset()
   {
   }
};

#endif