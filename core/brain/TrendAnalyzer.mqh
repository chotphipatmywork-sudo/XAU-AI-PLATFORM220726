//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TrendAnalyzer.mqh                                      |
//| Layer   : Brain                                                  |
//| Version : 3.2.0                                                  |
//| Purpose : Trend Package Facade                                   |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TRENDANALYZER_MQH
#define CORE_BRAIN_TRENDANALYZER_MQH

//--------------------------------------------------
// Trend Package
//--------------------------------------------------

#include "trend/config/TrendConfig.mqh"

#include "trend/models/TrendContext.mqh"
#include "trend/models/TrendWorkspace.mqh"
#include "trend/models/TrendResult.mqh"

#include "../indicators/models/IndicatorContext.mqh"
#include "../indicators/providers/ProviderManager.mqh"

#include "trend/engines/EMAEngine.mqh"
#include "trend/engines/SlopeEngine.mqh"
#include "trend/engines/StructureEngine.mqh"
#include "trend/engines/BOSEngine.mqh"
#include "trend/engines/CHOCHEngine.mqh"

#include "trend/assembler/TrendAssembler.mqh"

//--------------------------------------------------
// Trend Analyzer
//--------------------------------------------------

class CTrendAnalyzer
{
private:

   CTrendConfig m_config;

   CProviderManager m_providerManager;

   CEMAEngine       m_emaEngine;
   CSlopeEngine     m_slopeEngine;
   CStructureEngine m_structureEngine;
   CBOSEngine       m_bosEngine;
   CCHOCHEngine     m_chochEngine;

   CTrendAssembler  m_assembler;

public:

   //--------------------------------------------------

   void SetConfig(const CTrendConfig &config)
   {
      m_config = config;

      m_emaEngine.SetConfig(config);
      m_slopeEngine.SetConfig(config);
   }

   //--------------------------------------------------

   CTrendResult Analyze(const CTrendContext &context)
   {
      CTrendWorkspace workspace;

      workspace.Reset();

      workspace.Context = context;

      //------------------------------------------------
      // Build Indicator Context
      //------------------------------------------------

      CIndicatorContext indicatorContext;

      indicatorContext.Symbol    = context.Symbol;
      indicatorContext.Timeframe = context.Timeframe;
      indicatorContext.Bars      = context.Bars;

      indicatorContext.Shift     = context.Shift;

      //------------------------------------------------

      m_providerManager.SetContext(indicatorContext);
      m_providerManager.Update();

      //------------------------------------------------

      workspace.EMA =
         m_emaEngine.Analyze(m_providerManager);

      workspace.Slope =
         m_slopeEngine.Analyze(m_providerManager);

      workspace.ATR=
         m_providerManager.GetATR(m_config.ATRPeriod,0);

      workspace.FastEMALookback=
         m_providerManager.GetEMA(m_config.FastEMAPeriod,m_config.AITrendLookbackBars);
      
      workspace.Structure =
         m_structureEngine.Analyze(workspace.Slope);

      workspace.BOS =
         m_bosEngine.Analyze(workspace.Structure);

      workspace.CHOCH =
         m_chochEngine.Analyze(workspace.Structure);

      //------------------------------------------------

      return
         m_assembler.Assemble(
            workspace.EMA,
            workspace.Slope,
            workspace.Structure,
            workspace.BOS,
            workspace.CHOCH,
            workspace.ATR,
            workspace.FastEMALookback);
   }
};

#endif
