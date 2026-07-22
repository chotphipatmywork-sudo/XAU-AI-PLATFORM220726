//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestLiquidityEngine.mq5                                |
//| Layer   : Tests / Brain / Liquidity                              |
//| Version : 2.0.0                                                  |
//| Purpose : Directional Liquidity feature smoke test               |
//+------------------------------------------------------------------+

#property strict

#include "../core/brain/liquidity/engines/LiquidityEngine.mqh"

int OnInit()
  {
   CLiquidityContext context;
   context.Symbol=_Symbol;
   context.High=101.0;
   context.Low=95.0;
   context.Close=99.0;
   context.Volume=200.0;
   context.ReferenceHigh=100.0;
   context.ReferenceLow=90.0;
   context.AverageVolume=100.0;
   CLiquidityEngine engine;
   const CLiquidityResult result=engine.Analyze(context);
   const bool valid=(result.SweepDetected && result.BuySideSweep &&
                     !result.SellSideSweep &&
                     MathAbs(result.RangePosition-90.0)<0.000001 &&
                     MathAbs(result.SweepDirection-0.0)<0.000001);
   Print("Liquidity activity/range/sweep direction: ",result.Score,"/",
         result.RangePosition,"/",result.SweepDirection);
   Print("Directional liquidity feature valid: ",valid);
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
