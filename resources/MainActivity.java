package ${package_name};

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceRequest;
import android.view.View;
import com.google.android.gms.ads.MobileAds;
import com.google.android.gms.ads.initialization.InitializationStatus;
import com.google.android.gms.ads.initialization.OnInitializationCompleteListener;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdView;

public class MainActivity extends Activity {
    private String appId = "${app_id}";
    private String bannerPub = "$banner_pub";
    private String interstitialPub = "${interstitial_pub}";
    private AdView mAdView;
    private WebView mWebView;

    @Override   
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        if(appId != "ca-app-pub-3940256099942544~3347511713") {
            MobileAds.initialize(this, new OnInitializationCompleteListener() {
                @Override
                public void onInitializationComplete(InitializationStatus initializationStatus) {}
            });
            if(bannerPub != null && !bannerPub.trim().isEmpty()) {
                mAdView = findViewById(R.id.adView);
                AdRequest adRequest = new AdRequest.Builder().build();
                mAdView.loadAd(adRequest);
            }
            if(interstitialPub != null && !interstitialPub.trim().isEmpty()) {
                // load interstitial here later
            }
        }       
        mWebView = findViewById(R.id.activity_main_webview);
        WebSettings webSettings = mWebView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setAppCacheEnabled(true);
        webSettings.setDatabaseEnabled(true);
        webSettings.setAllowFileAccessFromFileURLs(true);
        webSettings.setAllowUniversalAccessFromFileURLs(true);
        mWebView.loadUrl("${url_path}");
        mWebView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                mWebView.loadUrl(request.getUrl().toString());
                return true;
            }
            
            @Override
            public void onPageFinished(WebView view, String url) {                
                new Handler().postDelayed(new Runnable(){
                    @Override
                    public void run() {
                        findViewById(R.id.splashscreen).setVisibility(View.GONE);
                        if(bannerPub != null && !bannerPub.trim().isEmpty()) {
                            findViewById(R.id.adView).setVisibility(View.VISIBLE);
                        } 
                        findViewById(R.id.activity_main_webview).setVisibility(View.VISIBLE);                 
                    }
                }, 1000);               
            }
        }); 
    }

    @Override
    public void onBackPressed() {
        if(mWebView.canGoBack()) {
            mWebView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
