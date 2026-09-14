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
import org.json.JSONObject;
import org.json.JSONException;
import java.util.Iterator;
import java.util.ArrayList;
import java.util.Arrays;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.File;
import java.io.IOException;
import java.io.UnsupportedEncodingException;


public class ImportPreferences extends Preference implements PreferenceManager.OnActivityResultListener {
	private static final int OPEN_FILE_REQUEST = 344;
	private Activity mActivity;
	private Context mContext;
	public ImportPreferences(Context context, AttributeSet attrs) {
		super(context, attrs);
	}
	public void setActivity(Activity activity)
	{
		mActivity = activity;
	}
	@Override
	public void onClick() {
		Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
		intent.putExtra(Intent.EXTRA_TITLE, "nhsettings.json");
		intent.setType("application/json");
		intent.addCategory(Intent.CATEGORY_OPENABLE);
		mActivity.startActivityForResult(intent, OPEN_FILE_REQUEST);
	}

	@Override
	public boolean onActivityResult(int requestCode, int resultCode, Intent data) {
		if (requestCode == OPEN_FILE_REQUEST) {
			if (resultCode == Activity.RESULT_OK) {
				try {
					InputStream is = getContext().getContentResolver().openInputStream(data.getData());
					byte[] bytes = readAllbytes(is);
					String jsonstr = new String(bytes);
					try {
						JSONObject jsonobj = new JSONObject(jsonstr);
						Iterator<String> keys = jsonobj.keys();
						SharedPreferences.Editor edit = getSharedPreferences().edit();
						while (keys.hasNext()) {
							String key = keys.next();
							if (key.equals("rcFileContents")) {
								File dir = new File(PreferenceManager.getDefaultSharedPreferences(getContext()).getString("datadir", ""));
								File rcFile = new File(dir, getContext().getResources().getString(R.string.defaultsFile));
								Uri rcUri = Uri.fromFile(rcFile);
								try {
									OutputStream os = getContext().getContentResolver().openOutputStream(rcUri, "wt");
									byte[] rcBytes = jsonobj.getString(key).getBytes();
									Log.print("rcFileContents bytes: " + new String(rcBytes));
									os.write(rcBytes);
									os.flush();
									os.close();
								} catch (IOException e) {
									Toast.makeText(getContext(), "failed to write file", Toast.LENGTH_LONG).show();
								}
							} else {
								Object obj = jsonobj.get(key);
								if (obj instanceof String) {
									edit.putString(key, (String)obj);
								} else if (obj instanceof Integer) {
									edit.putInt(key, (Integer)obj);
								} else if (obj instanceof Boolean) {
									edit.putBoolean(key, (Boolean)obj);
								}
							}
						}
						edit.apply();
						Toast.makeText(getContext(), "applied the new settings", Toast.LENGTH_LONG).show();
					} catch (JSONException e) {
						Toast.makeText(getContext(), "failed to read json", Toast.LENGTH_LONG).show();
					}
				} catch (IOException e) {
					Toast.makeText(getContext(), "failed to read file", Toast.LENGTH_LONG).show();
				}
			}
			// otherwise the settings menu will be in a weird state where the settings are set in SharedPreferences but not in the menus
			mActivity.finish();
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
