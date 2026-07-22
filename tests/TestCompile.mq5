//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestCompile.mq5                                        |
//| Purpose : Foundation compile verification                        |
//+------------------------------------------------------------------+
#property strict

//--------------------------------------------------
// Core
//--------------------------------------------------

#include "../core/interfaces/IModule.mqh"

#include "../core/infrastructure/Logger.mqh"
#include "../core/infrastructure/EventBus.mqh"

#include "../core/kernel/ModuleRegistry.mqh"
#include "../core/kernel/Kernel.mqh"
#include "../core/kernel/Application.mqh"

#include "../core/market/MarketData.mqh"

#include "../core/brain/Signal.mqh"
#include "../core/brain/Context.mqh"
#include "../core/brain/Decision.mqh"

//--------------------------------------------------

int OnInit()
{
   Print("Foundation Compile Passed");

   return INIT_SUCCEEDED;
}

//--------------------------------------------------

void OnTick()
{
}

//--------------------------------------------------

void OnDeinit(const int reason)
{
}