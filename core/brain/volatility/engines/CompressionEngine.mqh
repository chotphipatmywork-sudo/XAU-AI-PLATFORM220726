//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : CompressionEngine.mqh                                  |
//| Layer   : Brain / Volatility / Engines                           |
//| Version : 1.0.0                                                  |
//| Purpose : Volatility Compression Score Engine                    |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_VOLATILITY_ENGINES_COMPRESSIONENGINE_MQH
#define CORE_BRAIN_VOLATILITY_ENGINES_COMPRESSIONENGINE_MQH

class CCompressionEngine
{
public:
   double Analyze(const double ratio)
   {
      if(ratio>=1.0)
         return 0.0;
      return MathMax(0.0,MathMin(100.0,(1.0-ratio)*100.0));
   }
};

#endif
