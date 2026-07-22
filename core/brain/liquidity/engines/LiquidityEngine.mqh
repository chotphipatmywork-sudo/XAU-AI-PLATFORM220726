//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LiquidityEngine.mqh                                    |
//| Layer   : Brain / Liquidity / Engines                            |
//| Version : 1.1.0                                                  |
//| Purpose : Liquidity Analysis Engine                              |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_LIQUIDITY_ENGINES_LIQUIDITYENGINE_MQH
#define CORE_BRAIN_LIQUIDITY_ENGINES_LIQUIDITYENGINE_MQH

#include "../config/LiquidityConfig.mqh"
#include "../models/LiquidityContext.mqh"
#include "../models/LiquidityResult.mqh"

//--------------------------------------------------
// Liquidity Engine
//--------------------------------------------------

class CLiquidityEngine
{
private:

   CLiquidityConfig m_config;

public:

   //--------------------------------------------------

   void SetConfig(const CLiquidityConfig &config)
   {
      m_config = config;
   }

   //--------------------------------------------------

   CLiquidityResult Analyze(const CLiquidityContext &context)
   {
      CLiquidityResult result;
      result.Reset();

      if(context.High<=0.0 || context.Low<=0.0 ||
         context.ReferenceHigh<=0.0 || context.ReferenceLow<=0.0 ||
         context.AverageVolume<=0.0)
         return result;

      const double point=SymbolInfoDouble(context.Symbol,SYMBOL_POINT);
      const double tolerance=m_config.SweepTolerance*point;
      const double volume_ratio=context.Volume/context.AverageVolume;
      const bool high_sweep=(context.High>context.ReferenceHigh+tolerance &&
                             context.Close<context.ReferenceHigh);
      const bool low_sweep=(context.Low<context.ReferenceLow-tolerance &&
                            context.Close>context.ReferenceLow);

      result.BuySideLiquidity=(context.High>=context.ReferenceHigh-tolerance);
      result.SellSideLiquidity=(context.Low<=context.ReferenceLow+tolerance);
      result.SweepDetected=(high_sweep || low_sweep);
      result.BuySideSweep=high_sweep;
      result.SellSideSweep=low_sweep;
      const double reference_range=context.ReferenceHigh-context.ReferenceLow;
      if(reference_range>0.0)
         result.RangePosition=MathMax(0.0,MathMin(100.0,
            100.0*(context.Close-context.ReferenceLow)/reference_range));
      if(low_sweep && !high_sweep)
         result.SweepDirection=100.0;
      else if(high_sweep && !low_sweep)
         result.SweepDirection=0.0;
      else
         result.SweepDirection=50.0;
      result.Score=MathMin(100.0,50.0*volume_ratio);

      if(result.BuySideLiquidity || result.SellSideLiquidity)
         result.Score=MathMin(100.0,result.Score+10.0);

      if(result.SweepDetected)
        {
         result.State=LIQUIDITY_SWEEP;
         result.Score=100.0;
        }
      else if(volume_ratio>=1.50)
         result.State=LIQUIDITY_HIGH;
      else if(volume_ratio<=0.50)
         result.State=LIQUIDITY_LOW;
      else
         result.State=LIQUIDITY_NORMAL;

      result.Confidence=result.Score;

      return result;
   }
};

#endif
