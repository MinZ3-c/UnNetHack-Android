package com.tbd.forkfront;
import android.app.Activity;
import android.preference.Preference;
import android.preference.PreferenceManager;
import android.content.Intent;
import android.content.Context;
import android.content.SharedPreferences;
import android.util.AttributeSet;
import android.os.ParcelFileDescriptor;
import android.widget.Toast;
import android.net.Uri;
import android.content.res.Resources;
import org.json.JSONObject;
import org.json.JSONException;
import java.util.ArrayList;
import java.io.File;
import java.io.OutputStream;
import java.io.InputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.UnsupportedEncodingException;


public class ExportPreferences extends Preference implements PreferenceManager.OnActivityResultListener {
	private static final int CREATE_FILE_REQUEST = 343;
	private Activity mActivity;
	private Context mContext;
	public ExportPreferences(Context context, AttributeSet attrs) {
		super(context, attrs);
	}
	public void setActivity(Activity activity)
	{
		mActivity = activity;
	}
	@Override
	public void onClick() {
		Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
		intent.putExtra(Intent.EXTRA_TITLE, "nhsettings.json");
		intent.setType("application/json");
		intent.addCategory(Intent.CATEGORY_OPENABLE);
		mActivity.startActivityForResult(intent, CREATE_FILE_REQUEST);
	}

	@Override
	public boolean onActivityResult(int requestCode, int resultCode, Intent data) {
		if (requestCode == CREATE_FILE_REQUEST) {
			if (resultCode == Activity.RESULT_OK) {
				SharedPreferences prefs = getSharedPreferences();
				JSONObject jsonobj = new JSONObject();
				try {
					jsonobj.put("tileset", prefs.getString("tileset", "TTY"));
					jsonobj.put("tileW", prefs.getInt("tileW", 32));
					jsonobj.put("tileH", prefs.getInt("tileH", 32));
					jsonobj.put("customTileW", prefs.getInt("customTileW", 32));
					jsonobj.put("customTileH", prefs.getInt("customTileH", 32));

					jsonobj.put("fullscreen", prefs.getBoolean("fullscreen", false));
					jsonobj.put("immersive", prefs.getBoolean("immersive", false));
					jsonobj.put("monospace", prefs.getBoolean("monospace", false));
					jsonobj.put("lockView", prefs.getBoolean("lockView", false));
					jsonobj.put("fallbackRenderer", prefs.getBoolean("fallbackRenderer", false));

					jsonobj.put("hearseMail", prefs.getString("hearseMail", ""));
					jsonobj.put("hearseID", prefs.getString("hearseID", ""));
					jsonobj.put("hearseKeepUploaded", prefs.getBoolean("hearseKeepUploaded", false));
					jsonobj.put("hearseEnable", prefs.getBoolean("hearseEnabe", false));
					for (int i = 0; i <= 5; i++) {
						String key = String.format("pName%d", i);
						jsonobj.put(key, prefs.getString(key, i == 0 ? "Standard Panel" : String.format("Panel %d", i + 1)));
					}
					for (int i = 0; i <= 5; i++) {
						String key = String.format("pPortLoc%d", i);
						jsonobj.put(key, prefs.getString(key, "3"));
					}
					for (int i = 0; i <= 5; i++) {
						String key = String.format("pPortActive%d", i);
						jsonobj.put(key, prefs.getBoolean(key, i == 0 ? true : false));
					}
					for (int i = 0; i <= 5; i++) {
						String key = String.format("pLandLoc%d", i);
						jsonobj.put(key, prefs.getString(key, "3"));
					}
					for (int i = 0; i <= 5; i++) {
						String key = String.format("pLandActive%d", i);
						jsonobj.put(key, prefs.getBoolean(key, i == 0 ? true : false));
					}
					for (int i = 0; i <= 5; i++) {
						String key = String.format("pCmdString%d", i);
						jsonobj.put(key, prefs.getString(key, i == 0 ? getContext().getResources().getString(R.string.defaultCmdPanel) : ""));
					}
					for (int i = 0; i <= 5; i++) {
						String key = String.format("pOpacity%d", i);
						jsonobj.put(key, prefs.getInt(key, 255));
					}
					for (int i = 0; i <= 5; i++) {
						String key = String.format("pSize%d", i);
						jsonobj.put(key, prefs.getInt(key, 0));
					}
					jsonobj.put("ovlPortAlways", prefs.getBoolean("ovlPortAlways", false));
					jsonobj.put("ovlLandAlways", prefs.getBoolean("ovlLandAlways", false));
					jsonobj.put("ovlPortLoc", prefs.getString("ovlPortLoc", "1"));
					jsonobj.put("ovlLandLoc", prefs.getString("ovlLandLoc", "1"));
					jsonobj.put("allowMapDir", prefs.getBoolean("allowMapDir", false));

					jsonobj.put("backAction", prefs.getString("backAction", "0"));
					jsonobj.put("volup", prefs.getString("volup", "0"));
					jsonobj.put("voldown", prefs.getString("voldown", "0"));
					jsonobj.put("travelOnClick", prefs.getString("travelOnClick", "0"));

					jsonobj.put("statusOpacity", prefs.getInt("statusOpacity", 255));
					jsonobj.put("mapBorderOpacity", prefs.getInt("mapBorderOpacity", 50));
					jsonobj.put("ovlOpacity", prefs.getInt("ovlOpacity", 255));
					jsonobj.put("ovlSize", prefs.getInt("ovlSize", 0));

					File dir = new File(PreferenceManager.getDefaultSharedPreferences(getContext()).getString("datadir", ""));
					File rcFile = new File(dir, getContext().getResources().getString(R.string.defaultsFile));
					Uri rcUri = Uri.fromFile(rcFile);
					byte[] rcBytes;
					try {
						InputStream is = getContext().getContentResolver().openInputStream(rcUri);
						rcBytes = readAllbytes(is);
						is.close();
					} catch (FileNotFoundException e) {
						Toast.makeText(getContext(), "nethack rc file not found", Toast.LENGTH_LONG).show();
						rcBytes = "".getBytes();
					} catch (IOException e) {
						Toast.makeText(getContext(), "failed to read nethack rc file", Toast.LENGTH_LONG).show();
						rcBytes = "".getBytes();
					}
					String rcStr = new String(rcBytes);
					jsonobj.put("rcFileContents", rcStr);
				} catch (JSONException e) {
					Toast.makeText(getContext(), "failed to create settings json", Toast.LENGTH_LONG).show();
				}
				String str = jsonobj.toString();
				byte[] bytes;
				bytes = str.getBytes();
				try {
					OutputStream os = getContext().getContentResolver().openOutputStream(data.getData(), "wt");
					os.write(bytes);
					os.flush();
					os.close();
				} catch (IOException e) {
					Toast.makeText(getContext(), "failed to write settings file", Toast.LENGTH_LONG).show();
				}
			}
			return true;
		} else {
			return false;
		}
	}

	private byte[] readAllbytes(InputStream is) throws IOException {
		ArrayList<Byte> bytes = new ArrayList<Byte>();
		// TODO: make this not painfully slow :)
		while (true) {
			int read = is.read();
			if (read == -1) break;
			bytes.add((byte)read);
		}
		byte[] bytes_list = new byte[bytes.size()];
		for (int i = 0; i < bytes.size(); i++) {
			bytes_list[i] = bytes.get(i);
		}
		return bytes_list;
	}
}
