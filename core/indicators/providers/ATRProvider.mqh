//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ATRProvider.mqh                                        |
//| Layer   : Indicators / Providers                                 |
//| Version : 2.1.0                                                  |
//| Purpose : ATR Provider (Real MT5 Implementation)                 |
//+------------------------------------------------------------------+

#ifndef CORE_INDICATORS_PROVIDERS_ATRPROVIDER_MQH
#define CORE_INDICATORS_PROVIDERS_ATRPROVIDER_MQH

#include "../models/IndicatorContext.mqh"

class CATRProvider
{
private:

   CIndicatorContext m_context;

public:

   CATRProvider()
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
         iATR(
            m_context.Symbol,
            m_context.Timeframe,
            period);

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

   bool GetValues(
      const int period,
      const int start_shift,
      const int count,
      double &values[])
   {
      if(period<=0 || start_shift<0 || count<=0)
         return false;

      int handle=iATR(m_context.Symbol,m_context.Timeframe,period);
      if(handle==INVALID_HANDLE)
         return false;

      double buffer[];
      ArrayResize(buffer,count);
      if(CopyBuffer(handle,0,start_shift,count,buffer)!=count)
      {
         IndicatorRelease(handle);
         ArrayResize(values,0);
         return false;
      }
      ArrayResize(values,count);
      for(int index=0; index<count; index++)
         values[index]=buffer[count-1-index];
      IndicatorRelease(handle);
      return true;
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
